"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import json
from datetime import date
from unittest import TestCase
from tests.factories import AccountFactory
from service import talisman
from service.common import status  # HTTP Status Codes
from service.models import db, Account, DataValidationError, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_read_an_account(self):
        """It should GET a single Account by ID"""
        # 1) create one account
        account = AccountFactory()
        resp = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        account_id = resp.get_json()["id"]

        # 2) read that account
        resp = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], account_id)
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
        self.assertEqual(data["address"], account.address)
        self.assertEqual(data["phone_number"], account.phone_number)

    def test_read_account_not_found(self):
        """It should return 404_NOT_FOUND when the Account ID is missing"""
        resp = self.client.get(f"{BASE_URL}/0")        # ID 0 won't exist
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_account_happy_path(self):
        """It should GET a single account and return 200_OK"""
        # Arrange: create one record via the API
        account = AccountFactory()
        resp = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        account_id = resp.get_json()["id"]

        # Act: read it back
        resp = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Assert: payload integrity
        data = resp.get_json()
        self.assertEqual(data["id"], account_id)
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
        self.assertEqual(data["address"], account.address)
        self.assertEqual(data["phone_number"], account.phone_number)

    def test_read_account_bad_id_type(self):
        """It should return 404 (or 400) when the ID is not an int"""
        # Flask's <int:> converter will short-circuit anything non-numeric.
        resp = self.client.get(f"{BASE_URL}/abc")
        # Depending on your route setup this could be 404, 400, or 308 (redirect)
        self.assertIn(resp.status_code, [status.HTTP_404_NOT_FOUND,
                                        status.HTTP_400_BAD_REQUEST])

    def test_read_account_negative_id(self):
        """Edge case: negative integer returns 404_NOT_FOUND"""
        resp = self.client.get(f"{BASE_URL}/-1")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_repr_and_date_default(self):
        """Covers __init__, deserialize else-branch, and __repr__"""
        acc = Account()                       # hits PersistentBase.__init__
        acc.deserialize({
            "name": "Alice",
            "email": "alice@example.com",
            "address": "1 Elm St"
            # no date_joined → executes line 127
        })
        self.assertIn("<Account Alice", repr(acc))   # line 98
        self.assertEqual(acc.date_joined, date.today())

    def test_deserialize_key_error(self):
        """Covers DataValidationError branch (missing field)"""
        acc = Account()
        with self.assertRaises(DataValidationError) as ctx:
            acc.deserialize({"email": "no-name@example.com"})
        self.assertIn("missing name", str(ctx.exception))

class TestListAccounts(TestAccountService):
    def test_list_accounts_empty(self):
        """Listing accounts when none exist returns [] and 200"""
        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_list_accounts_non_empty(self):
        """Listing accounts when there are accounts returns them all"""
        # Create two accounts with the same helper you’ve used elsewhere
        post_data1 = {
            "name": "Bob", "email": "bob@example.com",
            "address": "2 Pine St", "phone_number": "555-0002"
        }
        post_data2 = {
            "name": "Carol", "email": "carol@example.com",
            "address": "3 Oak St", "phone_number": "555-0003"
        }
        r1 = self.client.post("/accounts", data=json.dumps(post_data1),
                              content_type="application/json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = self.client.post("/accounts", data=json.dumps(post_data2),
                              content_type="application/json")
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        names = {acct["name"] for acct in data}
        self.assertIn("Bob", names)
        self.assertIn("Carol", names)

class TestUpdateAccount(TestAccountService):
    def test_update_account_success(self):
        """ Update an existing account’s phone_number """
        post_data = {"name": "Dave", "email": "dave@example.com", "address": "4 Birch St", "phone_number": "555-0004"}
        r1 = self.client.post("/accounts", data=json.dumps(post_data), content_type="application/json")
        self.assertEquals(r1.status_code, status.HTTP_201_CREATED)
        account_id = r1.get_json()["id"]

        # Update only phone_number
        update_data = {"phone_number": "555-9999"}
        response = self.client.put(f"/accounts/{account_id}", 
                                   data=json.dumps(update_data), 
                                   content_type="application/json")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        updated = response.get_json()
        self.assertEquals(updated["id"], account_id)
        self.assertEquals(updated["phone_number"], "555-9999")

    def test_update_account_not_found(self):
        """ Update non-existent account returns 404 """
        update_data = {"phone_number": "555-9999"}
        response = self.client.put("/accounts/0", data=json.dumps(update_data), content_type="application/json")
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

class TestDeleteAccount(TestAccountService):
    def test_delete_account_success(self):
        """ Delete an existing account successfully """
        post_data = {"name": "Eve", "email": "eve@example.com", "address": "5 Cedar St", "phone_number": "555-0005"}
        r1 = self.client.post("/accounts", data=json.dumps(post_data), content_type="application/json")
        self.assertEquals(r1.status_code, status.HTTP_201_CREATED)
        account_id = r1.get_json()["id"]

        # Delete that account
        response = self.client.delete(f"/accounts/{account_id}")
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # Attempt to read it: should return 404
        response = self.client.get(f"/accounts/{account_id}")
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_not_found(self):
        """ Deleting a non-existent account should still return 204 """
        response = self.client.delete("/accounts/0")
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

class TestSecurityHeaders(TestCase):
    def setUp(self):
        from service import create_app, db, talisman
        self.app = create_app()
        self.client = self.app.test_client()
        talisman.force_https = False

    def test_security_headers_present(self):
        # request over https to root URL
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        headers = response.headers

        self.assertEqual(headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertIn("default-src 'self'; object-src 'none'", headers.get('Content-Security-Policy'))
        self.assertEqual(headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_cors_header_present(self):
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
