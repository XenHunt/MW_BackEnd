from flask_restful import reqparse

parserRegister = reqparse.RequestParser()
parserRegister.add_argument("username", required=True)
parserRegister.add_argument("password", required=True)
parserRegister.add_argument("firstName", required=False)
parserRegister.add_argument("lastName", required=False)
parserRegister.add_argument("role", required=True)

parserLogin = reqparse.RequestParser()
parserLogin.add_argument("username", required=True)
parserLogin.add_argument("password", required=True)

parserId = reqparse.RequestParser()
parserId.add_argument("uid", required=True)
parserId.add_argument("system_string", required=True)
parserId.add_argument(
    "access_token",
    required=False,
)

parserUpdate = reqparse.RequestParser()
parserUpdate.add_argument("username", required=False)
parserUpdate.add_argument("password", required=False)
parserUpdate.add_argument("firstName", required=False)
parserUpdate.add_argument("lastName", required=False)
parserUpdate.add_argument("role", required=False)
parserUpdate.add_argument("id", required=True)

parserCustomer = reqparse.RequestParser()
parserCustomer.add_argument("firstName", required=True)
parserCustomer.add_argument("lastName", required=True)
parserCustomer.add_argument("email")
parserCustomer.add_argument("phone")

parserMeeting = reqparse.RequestParser()
parserMeeting.add_argument("address")
parserMeeting.add_argument("description")


parserCustomerMeeting = reqparse.RequestParser()
