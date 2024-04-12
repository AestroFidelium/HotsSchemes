The following schemas were created utilizing all available files from Heroes of the Storm. Additionally, a secondary schema was developed by combining resources from both Heroes of the Storm and Starcraft II; however, the accuracy of this schema may not be guaranteed.

Below is the code for the universal Heroes of the Storm schema, which is designed to be compatible with catalog trees, descriptions, or any other similar applications. For instance:


```xml
<?xml version="1.0" encoding="utf-8"?>
<Catalog xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/AestroFidelium/HotsSchemes/master/Universal-Hots.xsd">
	
</Catalog>
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<tree xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/AestroFidelium/HotsSchemes/master/Universal-Hots.xsd">
	
</tree>
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<Desc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/AestroFidelium/HotsSchemes/master/Universal-Hots.xsd">
	
</Desc>
```



The essence of the schemas I have generated is that they demonstrate which function parameters are most frequently received. If there are many parameters, the schema will output 150 examples, which should be sufficient to accurately determine what specifically should be used.

For instance, within the function Range, it will respond with `<Range value="Any Float" />`, implying that any float number can be used. Conversely, if you write `<Effect value="UniqueValue" />`, the UniqueValue field will contain 150 different usage variants. It is also worth noting that I have limited the number of examples in the 'id' field to 35 to reduce the load.

There are plans to generate a description for each function based on the game files, although no specific date has been set for this yet.