"""API Client Usage Examples.

Shows different ways to initialize and use the Phase to Phase API client.
"""

from pyptp import Client, Credentials

# Method 1: From environment variables
# Requires PYPTP_CLIENT_ID and PYPTP_CLIENT_SECRET set in environment
client = Client()

# Method 2: Using Credentials object
creds = Credentials(client_id="your-client-id", client_secret="your-secret")
client = Client(credentials=creds)

# Method 3: Direct parameters
client = Client(client_id="your-client-id", client_secret="your-secret")

# Method 4: For specific environment (acceptance/test/production)
client = Client.for_environment(
    "acceptance",
    client_id="your-client-id",
    client_secret="your-secret",
)

# Using the client (future implementation)
# token = client.get_token()
# networks = client.list_networks()
