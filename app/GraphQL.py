from graphene import ObjectType, String, Schema

class Query(ObjectType):
    hello = String(first_name = String(default_value='stranger'))
    goodbye = String()
    
    def resolve_hello(root, info, first_name):
        return f'Helllo {first_name}!'
    
    def resolve_goodbye(root, info):
        return f'See ya!'
    

schema = Schema(query = Query)

request = '{ goodbye }'
result = schema.execute(request)
print(result.data)