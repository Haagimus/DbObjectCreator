from simple_salesforce import SalesforceLogin, Salesforce


class SFObject:
    """
    This class outlines a generic SalesForce object that can then be used to store necessary properties for use in
    other methods.

    Yields
    ----------
    SFObject
        A Salesforce class object
    """
    def __init__(self, username, password, token, session_id=None, instance=None, connection=None):
        """Create a new :class:`.SFObject` instance.

        Summary
        ----------
        This will create an SFObject which contains all necessary properties and methods to interact with a Salesforce
        server.

        Parameters
        ----------
        username: str
            This is the username for the Salesforce account.
        password : str
            This is the password for the Salesforce account.
        token : str
            This is the token for the Salesforce account. If you do not have this you can generate or reset this in
            your account by going to your account settings and selecting the "Reset My Security Token" menu option
            under "My Personal Information" in the right side navigation menu.
        session_id : str
            This is the session_id assigned after logging into your account.
        instance : str
            This is the instance address, which becomes available after logging into your account.
        connection : Salesforce
            This is the database host address.
        """
        self.username: str = username
        self.password: str = password
        self.token: str = token
        self.session_id: str = session_id
        self.instance: str = instance
        self.connection: Salesforce = connection

    def server_login(self):
        """
        Attempts to establish a connection to the Salesforce server using username, password and
        token. If successful the returned session_id and instance will be used to establish a connection.
        The corresponding object properties will be set for each item.

        Returns
        ----------
        None
        """
        try:
            self.session_id, self.instance = SalesforceLogin(
                username=self.username,
                password=self.password,
                security_token=self.token,
                client_id='Data Lake Project Application')
            self.establish_connection()
        except Exception as e:
            raise SFObjectError(e)

    def establish_connection(self):
        """
        Attempts to connect to a Salesforce server using instance and session_id. If successful the self.connection
        property of the object is set.

        Returns
        ----------
        None
        """
        try:
            self.connection = Salesforce(instance=self.instance,
                                         session_id=self.session_id)
        except Exception as e:
            raise SFObjectError(e)

    def close_session(self):
        try:
            self.connection.session.close()
        except Exception as e:
            raise SFObjectError(e)


class SFObjectError(Exception):
    """A custom exception handler for internal errors."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'SFObjectError, {self.message}'
        else:
            return 'SFObjectError has been raised'
