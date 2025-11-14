import ast #true eval
import os #File name
import json #JSON Conversion
from urllib.parse import quote, unquote #URL-Encoding
from datetime import datetime #Tick counting
from pathlib import Path #Clicking on folder path
from requests import get, put, patch, delete #HTTP Requests

debug = True

def dprint(*args):
     if debug:
          print(*args)

class FirebaseTools:
     def __init__(self, dbLink: str, dbKey: str):             
        self.defaultLink =  'DATABASE_REFERENCE_URL'
        self.dbKey = 'DATABASE_SECRET'

        if dbLink:
             self.defaultLink = dbLink
        if dbKey:
             self.dbKey = dbKey

        self.dbLink = self.defaultLink
        self.linkEnd = '.json?auth=' + self.dbKey
        self.localDB = self.getData(False) or {}
        dprint('INITIATED FIREBASE TOOLS\n')
     
     def getPath(self, nodeName: str):
          return self.dbLink + quote(nodeName)  # make it web friendly    
     
     def setPath(self, nodeName: str):
          if nodeName != '':
               if self.getValue(nodeName, '', False):
                    self.dbLink = self.defaultLink + quote(nodeName) + '/'
                    dprint('Changed Firebase Path to:', self.dbLink)
                    return True     
               dprint(f'ERROR: Tried setting self.dbLink to {nodeName} however it does not exist!')   
               return False
          else:
               self.dbLink = self.defaultLink            

     def setValue(self, nodeName: str, key: str, value: any, stringFormat : bool):
          if not nodeName:
               dprint(f'ERROR: setValue did not receive nodeName!')
               return False
          nodeData = self.getValue(nodeName, '', False)#Grabbing as dictioanry makes it easier to set data for other things + prevents double formatting for stringFormat
          clearNode = False
          amendNode = False
          #note to self: I had a shorter version of this but this is technically more efficient/uses patch and delete instead of put for everything

          if not nodeData and key and value: #Create the node
               if stringFormat:
                    value = str(value)

               nodeData = {key: value}
               self.localDB[nodeName] = nodeData
               dprint(f'Creating: Node \"{nodeName}\"')
          elif nodeData and (isinstance(nodeData, list) or isinstance(nodeData, dict)) and key in nodeData: #Arrayed List + Key exists - Change the old key
               newInfo = {key: value} 
               if stringFormat:
                    newInfo = {key: str(value)}
               nodeData = {**nodeData, **newInfo}
                              
               self.localDB[nodeName] = nodeData
          elif not key and value: #No Key, Got Value - Overwrite
               nodeData = value

               if stringFormat:
                    nodeData = str(nodeData) 
               self.localDB[nodeName] = nodeData
          elif not key and value == None: #No Key No Value - Wipe
               clearNode = True
               self.localDB[nodeName] = None
               dprint(f'Cleared {nodeName} from localDB', self.localDB)
          else: #Amend the node with new key
               amendNode = True
               if stringFormat:
                    value = str(value)

               newInfo = {key: value} 
               indexedND = {nodeName: nodeData}

               if not (isinstance(nodeData, list) or isinstance(nodeData, dict)): #its a string or integer, 
                    nodeData = {**indexedND, **newInfo}  
                    merged = nodeData 
               else:
                    nodeData = newInfo
                    merged = {**nodeData, **newInfo}

               self.localDB[nodeName] = merged          

          if clearNode:
               data = delete(self.getPath(nodeName) + self.linkEnd)
          elif amendNode:
               data = patch(self.getPath(nodeName) + self.linkEnd, json=nodeData)
          else:
               data = put(self.getPath(nodeName) + self.linkEnd, json=nodeData)

          if data.status_code != 200:
               dprint(f"Error Setting Value: {data.status_code}")
               return False
          return True       
     
     def getValue(self, nodeName: str, key: str, stringFormat: bool):
          data = get(self.getPath(nodeName + '/' + key) + self.linkEnd)        
          if data.status_code == 200:
               receivedData = data.json()
               dprint('Received Data:', receivedData)
               if receivedData is not None:
                    if type(receivedData) == str:
                         string = receivedData
                         try:
                              formatted = json.loads(receivedData)
                              dprint('nodeData as:', receivedData, type(receivedData))
                         except json.JSONDecodeError as e:
                              formatted = ast.literal_eval(receivedData)
                              dprint('Converted nodeData using literal_eval:', receivedData, type(receivedData))
                    else:
                         formatted = receivedData
                         string = json.dumps(receivedData)  
                    return stringFormat and string or formatted
               else:
                    return stringFormat and 'null' or None     
          else:
               match data.status_code:
                    case 401:
                         raise Exception(f"ERROR: HTTP 401 while trying to access Node: \"{nodeName}\" Key: \"{key}\" - Database Key is invalid.")
                    case _:
                         raise Exception(f"ERROR: Cannot get Node: \"{nodeName}\" Key: \"{key}\" Code: {data.status_code}")           
     
     def removeValue(self, nodeName: str, key: str):
          if self.getValue(nodeName, key, False):
               dprint(f'Removed Node: \"{nodeName}\" -> Key: \"{key}\"!')
               return self.setValue(nodeName, key, None, False)
          dprint(f'ERROR: removeValue tried to remove: Value \"{key}\" however it does not exist!')
          return False

     def createNode(self, nodeName: str, key: str, value: any):
          if not self.getValue(nodeName, '', False):
               dprint(f'Created: Node \"{nodeName}\"!')
               return self.setValue(nodeName, key, value or 'Value', False)
          dprint(f'ERROR: createNode tried to create: Node \"{nodeName}\" however it already exists!')
          return False
     
     def getNode(self, nodeName: str, stringFormat: bool):
          if self.getValue(nodeName, '', False):
               dprint(f'Getting Node data: {nodeName}')
               return self.getValue(nodeName, '', stringFormat)          
          dprint(f'ERROR: getNode tried to get data from: Node \"{nodeName}\" however it does not exist!' )
          return False

     def overwriteNode(self, nodeName: str, value: any, stringFormat: bool):
          if self.getValue(nodeName, '', False):
               return self.setValue(nodeName, '', value, stringFormat)
          dprint(f'ERROR: overwriteNode tried to overwrite: Node \"{nodeName}\" however it does not exist!')
          return False

     def getNodeNames(self):
          nodes = self.localDB or self.getData(False)
          if nodes:
               return list(nodes.keys())
          return {}

     def removeNode(self, nodeName: str):
          if self.getValue(nodeName, '', False):
               dprint(f'Node {nodeName} removed!')
               return self.removeValue(nodeName, '')
          dprint(f'ERROR: removeNode tried to remove: Node \"{nodeName}\" however it does not exist!')
          return False
     
     def removeNodes(self, nodes: list):
          for nodeName in nodes:
               self.removeNode(nodeName) 

     def getData(self, stringFormat: bool):
          dprint('Receiving entire data')
          startTime = datetime.now()
          data = self.getValue('', '', stringFormat)
          dprint(f'Received data in: {(datetime.now() - startTime).total_seconds()} seconds')
          return data
     
     def backupData(self, path: str, fileName: str):
          if not path or not os.path.exists(path):
               path = os.path.join(os.getcwd(), 'FirebaseBackups')
               os.makedirs(path, exist_ok=True)
               dprint(f'New path set as: {path}')

          if not fileName or fileName == '':
               time = datetime.now().strftime('%Y-%m-%d - %H-%M-%S')#Format time
               fileName = 'FirebaseBackup - '+time

          dbData = self.localDB or self.getData(False)
          with open(os.path.join(path, f'{fileName}.json'), 'w') as file:
               try:
                    json.dump(dbData, file, indent=4)
                    folderPath = Path(os.path.dirname(file.name)).resolve().as_uri()
                    dprint(f'Firebase data {self.dbLink} backed up to path: \n {folderPath}')
               except Exception as error:
                    dprint(f'ERROR: backupData tried to back up to {file.name} but encountered an error: {error}.')
               file.close()
               
     def wipeData(self, backup: bool, path: str, fileName: str):
          if backup:
               self.backupData(path, fileName)
          self.removeNodes(self.getNodeNames())
          dprint(f'Firebase: {self.dbLink} wiped!')
     

if __name__ == "__main__":
     fb = FirebaseTools('', '')

