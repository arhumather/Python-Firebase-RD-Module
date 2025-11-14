# Python Firebase RD Module v1.0.0 #
#### Created by Arhum Ather

## Description

The Python Firebase RD (Realtime Database) Module is a custom module designed for accessing and updating nodes in the Realtime Database to and from Google's Firebase using the [REST API](https://firebase.google.com/docs/database/rest/start). 

It includes features such as:

### v1.0.0 - Initial Release

- Receiving list data (`self.getValue`)
- Updating list data (`self.setValue`)
- Deleting list data (`self.removeValue`)

- Creating node data (`self.createNode`)
- Receiving node data (`self.getNode`, `self.getNodeNames`)
- Updating node data (`self.ovewriteNode`, `self.removeNode`, `self.removeNodes`)

- Downloading entire database data (`self.backupData`)
- Wiping entire database data (`self.wipeData`)

- Having a local dictionary of the database (`self.localDB`)

This was initally created out of curiosity and exploring more about using HTTP Requests with Firebase, and a cleaner alternative to the [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup), in my opinion, but it is also going to be used in my [Classic Flow NEA Project]() and free for open-source use.
## Recommendations/Tips

1) Set `debug` to True if you want to output useful prints and for debugging. However, keep in mind the larger the database, the longer it would take for it to output, so comment the prints, most of which are in `self.getValue`.

    - Especially for using functions such as `self.getData` where the entire database is being returned.

2) Modify `os.getcwd()` beforehand to change the current directory, this folder is where backups are saved to by default.

    - Use `oc.chdir(new_path)`

3) Make sure you have user permissions set up in Firebase rules; if you wish to have this module in a game or project where users have this downloaded. This is so users can't update nodes they shouldn't have access to. 
    - Read more at: [Firebase Realtime Database Security Rules](https://firebase.google.com/docs/database/security)

4) When using `self.localDB`, keep in mind changes from the database outside of your program could not appear. It would be recommended to update it at regular intervals using `self.getNodes(False)` to keep it up-to-date.

5) Feel free to fork this or use for your own projects, I'm open to edits and improvements but make sure to credit me as it would be very much appreciated! 
## Setup
To begin, copy your database link and API key and paste into the variables inside the `__init__` procedure:

```py
self.dbLink = 'https://www.exampleproject-default-rtdb.firebaseio.com/'
self.dbKey = 'DATABASE_KEY'
```
To use this module in another script you would import it as follows:

```py
#Assume that fbTools.py is the name of the file, it must also be in the same directory as the file you are writing in.
from fbTools import FirebaseTools
fb = FirebaseTools('', '')
```

## Assumptions

For demonstration purposes below, we will assume any variables for the functions and procedures are, hypothetically, of the following:

The database is stored as:

```JSON
{
    "TestNode": {
        "TestKey": "Value"
    },
    "TestNode2": {
        "TestKey1": "TestValue1",
        "TestKey2": 55
    },
    "TestNode3": 20
}
```

`os.getcwd()` is set as: `C:\Users\CurrentUser\`

`fb` is set as:

```py
fb = FirebaseTools('', '')
```

The time and date is:

**Date**: 31/01/2025

**Time**: 00:12:30
## Functions Usage
## \_\_init\_\_

`dbLink`: The database reference url to access the Realtime Database. 

- If set as an empty string: it will remain as what is stored in `self.dbLink`.

`dbKey`: The database secret key to access the Realtime Database
- Read more at [Database Secrets](https://firebase.google.com/docs/auth/web/custom-auth?authuser=0#return-custom-tokens-from-your-authentication-server)

- If set to an empty string: it will remain as what is stored in `self.dbKey`.

This initiates the variables and sets up localDB to mock the database online and have an easier access through dictionary. 

- In the unlikely case that either `self.dbLink` or `self.dbKey` are incorrect, a HTTP 401 error is raised in which a custom error message appears.
```py
#__init__
fb = FirebaseTools('', '')
#self.defaultLink and self.dbKey remains the same.
fb = FirebaseTools('https://www.newwebsite.com/', 'newwebsitedbkey')
#Sets self.defaultLink to 'https://www.newwebsite.com/'
#Sets self.dbKey to 'newwebsitedbkey'
```
## getPath
`name`: Desired node you wish to access.

This returns a path that formats `name` with percent-encoding and ammends to self.dbLink. (This is used for the other functions to handle sending HTTP Requests.)

```py
#getPath
path = fb.getPath('TestNode')
#Returns: 'https://www.exampleproject-default-rtdb.firebaseio.com/TestNode'
```
## setPath

`nodeName:` Name of the node you are setting the path to.

This sets the database link to the chosen node path. (This can be done if you want to only access a specific node.)

```py
#setPath
fb.setPath('TestNode2')
#Returns True
#Database path would be set as: {"TestKey1": "TestValue1",    "TestKey2": 55}
```
## setValue

`nodeName`: Name of the root-node, in the current path, you wish to update the value in.

- In the case the data in the node is not a dictionary, for example a string or an integer, a dictionary will be created in which the key is the `nodeName` and the value is the `nodeData`, it will then add the inputted key and value seperately.

- Setting this to a node that does not exist will create a new node for you. 
  - This is easier to achieve with `self.createNode`.

`key`: Name of the key you are updating.

- If this is set as an empty string, it will overwrite the entire node with what is set in `value`.

`value`: New value set to key. 

- Setting key as an empty string and setting value as an empty string will delete the entire node. 
  - This is easier to achieve with `self.removeNode`.

`stringFormat`: Upload the value as a string or a formatted dictionary/list.

This sets the `value` to the `key` attribute in the node under `nodeName` effectively creating a key and value dictionary. This also creates and updates nodes through other methods depending on the variables set in key and value.

```py
#setValue 

#Key, Value, JSON
fb.setValue('TestNode', 'TestKey', 'TestValue', False)
#TestNode is set as: {"TestKey" : "TestValue"}

#Key, Value, JSON - Amending to a node that is a dictionary/list.
fb.setValue('TestNode2', 'TestKey3', 'Value', True)
#TestNode3 is set as: "{'TestKey1': 'TestValue1', 'TestKey2': 55, 'TestKey3': 'Value'}"

#Key, Value, JSON - Amending to a unary node that is not a dictionary/list.
fb.setValue('TestNode3', 'NewKey', [1, 2], False)
#TestNode3 is set as: {"NewKey": [1, 2], "TestNode3": 2}

#No Key, No Value
fb.setValue('TestNode3', '', '', False)
#TestNode3 is set as: None

#No Key, One Value
fb.setValue('TestNode2', '', {"Test" : 5}, False)
#TestNode2 is set as: {"Test" : 5}
```
## getValue
`nodeName`: Name of the root-node, in the current path, you wish to receive the value from.

`key`: Name of the key you are accessing. 

- Setting this as an empty string will return the whole node data. 
  - This is easier to achieve with `self.getNode`.

`stringFormat`: Receive the value as a string or formmated (dictionary/list).

This returns the value for the key stored in the node `nodeName`.

```py
#getValue

#Key, JSON Format
fb.getValue('TestNode', 'TestKey', False)
#Returns: "Value"

#No Key, String Format
fb.getValue('TestNode2', '', True)
#Returns {"TestKey1": "TestValue1", "TestKey2": 55}
```
## removeValue

`nodeName`: Name of the root-node, in the current path, you wish to remove the value from.

`key`: Name of the key you are removing the value from. 

- Setting this to an empty string will remove the key from the node of `nodeName`. 

- If `key` is set to an empty string: it will remove the entire node. 
  - This is easier to achieve with `self.removeNode`.

```py
#removeValue
fb.removeValue('TestNode2', 'TestKey2')
#TestNode2 is set as: {"TestKey1": "TestValue1"}
```
## createNode

`nodeName`: Name of the root-node you wish to create, in the current path.

`key`: Name of the key you are creating.

- If you set as an empty string: it will create a unary node with only one value.

`value`: New value set to key in node.

This creates a new node with a key and value as a root-node, or in the current path as a sub-node.

```py
#createNode
fb.createNode('MyNewNode', '', {"Key": "Value"}, True)
#Database is set as: {"TestNode": {"TestKey": "Value"},"TestNode2": {"TestKey1": "TestValue1", "TestKey2": 55}, "TestNode3": 20, "MyNewNode" : "{"Key": "Value"}"}
```
## getNode

`nodeName`: Name of the root-node, in the current path, you wish to receive the value from.

- If you set this to an empty string: it will return the database's entire nodes and sub-nodes.
  
  - This is easier to achieve with `self.getData`. 

`stringFormat`: Receive the value as a string or formmated dictionary/list.

This returns the data from a specific node.

```py
#getNode
fb.getNode('TestNode3', True)
#Returns: "20"
fb.getNode('TestNode', False)
#Returns {"TestKey": "Value"}
```
## ovewriteNode

`nodeName`: Name of the root-node, in the current path, you wish to update the value in.

`value`: New value set to node.
- If set to an empty string: this will remove the nodes and delete the node from the database.
  - This is easier to achieve with `self.removeNode`.

`stringFormat`: Updates the value as a string or formmated dictionary/list.

This overwrites the node entirely with whatever is set as `value`.
```py
#ovewriteNode
fb.overwriteNode('TestNode', [1, 2, 3, 4, 5], True)
#TestNode is set as: "[1, 2, 3, 4, 5]"
```
## getNodeNames

This returns the names of all the root-nodes in the database as a list.

```py
#getNodeNames
fb.getNodeNames()
#Returns: ['TestNode', 'TestNode2', 'TestNode3']
```
## removeNode

`nodeName`: Name of the root-node, in the current path, you wish to remove the value from.

- If set to an empty string, it will remove the entire database of data. This is easier to achieve with `self.wipeData`.

```py
#removeNode
fb.removeNode('TestNode2')
#Database is set as: {"TestNode": {"TestKey": "Value"}, "TestNode3": 20}
```
## removeNodes
`nodes`: List of node names you wish to remove.

This deletes the nodes from the `nodes` list including all the sub-keys and values.

```py
#removeNodes
fb.removeNodes(['TestNode', 'TestNode2'])
#Database would be: {"TestNode3" : 20}
```
## getData

`stringFormat`: Receive the value as a string or formmated dictionary/list.

This returns the data for every node, essentially the entire database.
```py
#getData
fb.getData(False)
#Returns: {"TestNode": {"TestKey": "Value"},"TestNode2": {"TestKey1": "TestValue1", "TestKey2": 55}, "TestNode3": 20}
fb.getData(True)
#Returns: "{"TestNode": {"TestKey": "Value"},"TestNode2": {"TestKey1": "TestValue1", "TestKey2": 55}, "TestNode3": 20}"
```
## backupData

`path`: The path you would like to save the file to.

- Any backward slashes `\` would have to be replaced with forward slashes `/`. 
- If it is left as an empty string or an invalid path, it will be saved to the current directory at `os.getcwd()`.

`fileName`: The name you would like the JSON file to be saved as. 

- If set as an empty string: it will save with "FirebaseBackup" joined with a formatted date time string.

This will download the entire database locally as a .JSON file. Larger files tend to take longer to back up.

```py
#backupData

#Custom Path, Custom Name
fb.backupData("C:/Users/CurrentUser/Documents/MyPath", 'Backup')
#Saves the database as 'Backup.json' to: C:\Users\CurrentUser\Documents\MyPath"

#No Path, Custom Name
fb.backupData('', 'Backup')
#Saves the database as 'Backup.json' to: C:\Users\CurrentUser\

#No Path, No Name
fb.backupData('', '')
#Saves the database as 'FirebaseBackup - 2025-01-31 00-12-31.json' to: C:\Users\CurrentUser\Documents\MyPath"
```
## wipeData

`backup`: Boolean deciding if data is backed up before wiping.

- If set to True: data will be backed up before wiping. 
- If Set to False: data will not be backed up before wiping.

`path`: The path you would like to back up the file to.
- If `backup` is true: the data will be stored to this path.
-  If `path` is left as an empty string or is invalid, data will be stored to the current directory at `os.getcwd()`.

`fileName`: The name you would like the JSON file to be saved as. 
- If `backup` is true: the data will be stored with this fileName.
- If `fileName` is left as an empty string, the fileName will be set to "FirebaseBackup" joined with a formatted date time string.

This will completely wipe the whole database removing every node and sub-nodes. It is recommended to use with caution, back up data beforehand and set up rules to prevent unauthorized users from wiping. 

```py
fb.wipeData(True, 'C:/Users/CurrentUser/Documents/MyPath', 'Backup')
#Backup data with the name 'Backup.json' to C:\Users\CurrentUser\Documents\MyPath

fb.wipeData(False, '', '')
print(self.getData(False))
#Outputs None
```
