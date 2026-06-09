This app is a mechanic shop API.

It features app factory features, utilizes SQLAlchemy 2.x, Marshmallow and Flask

tables have 1 to many and many to many relationships

Updated 6/4/26.

This mechanic shop API features JWT authentication, rate limiting and caching. 

It now features a junction table for linking inventory items to service tickets, the ability to add
and remove mechanics from tickets using their IDs, sorting tickets by the most popular mechanic, 
and finding all tickets for a specific customer ID.

Updated 6/8/26

The mechanic shop API now features full SWAGGER documentaion for each route.

Each route also contains a unit test to test functionality, including negative tests to make sure the routes are functioning correctly.
