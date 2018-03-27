# Define the data types that can be used
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
    }
}
# Define the names that can be used to retrieve columns for combo box inputs
column_d_type_maps = {
    "column_numeric":["int","float"],
    "column":list(types.keys())
}