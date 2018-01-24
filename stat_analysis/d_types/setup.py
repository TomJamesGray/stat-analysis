# Define the data types that can be used
# TODO implement format attributes for types like datetime
types = {
    "int":{
        # Convert to float first otherwise error is raised for values with decimals
        "convert":lambda x:int(float(x))
    },
    "float":{
        "convert":lambda x:float(x)
    },
    "string":{
        "convert":lambda x:str(x)
    },
    "datetime":{
        "convert":lambda x,fmt:str(x),
        "format_required":True
    }
}

column_d_type_maps = {
    "column_numeric":["int","float"],
    "column":list(types.keys())
}