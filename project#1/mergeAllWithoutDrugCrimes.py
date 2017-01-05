
# coding: utf-8

# In[1]:

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class mergeAllWithoutDrugCrimes(dml.Algorithm):
    contributor = 'aditid_benli95_teayoon_tyao'
    reads = ['aditid_benli95_teayoon_tyao.crimesLegacy', 'aditid_benli95_teayoon_tyao.crimesCurrent']
    writes = ['aditid_benli95_teayoon_tyao.noDrugCrimesMaster']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aditid_benli95_teayoon_tyao', 'aditid_benli95_teayoon_tyao')

        repo.dropPermanent('aditid_benli95_teayoon_tyao.noDrugCrimesMaster')
        repo.createPermanent('aditid_benli95_teayoon_tyao.noDrugCrimesMaster')

        data = repo.aditid_benli95_teayoon_tyao.crimesLegacy.find()
        for document in data:
            legacyDict = dict(document)
            if legacyDict['incident_type_description'] == 'Drug Violation' or legacyDict['incident_type_description'] == 'DRUG CHARGES':
                continue
            else:

                if legacyDict['location']['coordinates'][1] == 0 or legacyDict['location']['coordinates'][0] == 0:
                    pass

                elif legacyDict['location']['coordinates'] and legacyDict['fromdate'] and legacyDict['day_week']:
                    dateAndTime = legacyDict['fromdate'].split("T")
                    date = dateAndTime[0].split("-")
                    time = dateAndTime[1].split(":")
                    date = date[1] + "/" + date[2] + "/" + date[0]
                    time = time[0] + ":" + time[1]
                    dateAndTime = date + " " + time
                    
                    entry = {'date':dateAndTime,'day':legacyDict['day_week'], 'latitude':legacyDict['location']['coordinates'][1], 'longitude':legacyDict['location']['coordinates'][0]}

                    res = repo.aditid_benli95_teayoon_tyao.noDrugCrimesMaster.insert_one(entry)

        data = repo.aditid_benli95_teayoon_tyao.crimesCurrent.find()
        for document in data:
            currentDict = dict(document)
            
            if currentDict['offense_code_group'] == 'Drug Violation':
                continue
                
            else:
                if currentDict['location']['coordinates'][1] == 0 or currentDict['location']['coordinates'][0] == 0:
                    pass
                elif currentDict['occurred_on_date'] and currentDict['day_of_week']:
                    dateAndTime = currentDict['occurred_on_date'].split("T")
                    date = dateAndTime[0].split("-")
                    time = dateAndTime[1].split(":")
                    date = date[1] + "/" + date[2] + "/" + date[0]
                    time = time[0] + ":" + time[1]
                    dateAndTime = date + " " + time

                    try:
                        latitude = currentDict['location_2']['coordinates'][0]
                        longitude = currentDict['location_2']['coordinates'][1]
                        entry = {'date':dateAndTime, 'day':currentDict['day_of_week'], 'latitude':latitude, 'longitude':longitude}
                        res = repo.aditid_benli95_teayoon_tyao.noDrugCrimesMaster.insert_one(entry)
                    
                    except:
                        pass

        endTime = datetime.datetime.now()
        return {"Start ":startTime, "End ":endTime}

            
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aditid_benli95_teayoon_tyao', 'aditid_benli95_teayoon_tyao')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('cob', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bod', 'http://bostonopendata.boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:aditid_benli95_teayoon_tyao#mergeCrimes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        mergeCRI = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {'prov:label':'Merge Crime Data', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(mergeCRI, this_script)
        
        resource_crimesLegacy = doc.entity('dat:aditid_benli95_teayoon_tyao#crimesLegacy', {'prov:label':'Past Crime Incident Reports', prov.model.PROV_TYPE:'ont:Dataset'})
        doc.usage(mergeCRI, resource_crimesLegacy, startTime)

        resource_crimesCurrent = doc.entity('dat:aditid_benli95_teayoon_tyao#crimesCurrent', {'prov:label':'Current Crime Incident Reports', prov.model.PROV_TYPE:'ont:Dataset'})
        doc.usage(mergeCRI, resource_crimesCurrent, startTime)

        noDrugCrimesMaster = doc.entity('dat:aditid_benli95_teayoon_tyao#noDrugCrimesMaster', {'prov:label':'All Non-Drug Crime Incident Reports', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(noDrugCrimesMaster, this_script)
        doc.wasGeneratedBy(noDrugCrimesMaster, mergeCRI, endTime)
        doc.wasDerivedFrom(noDrugCrimesMaster, resource_crimesLegacy, mergeCRI, mergeCRI, mergeCRI)
        doc.wasDerivedFrom(noDrugCrimesMaster, resource_crimesCurrent, mergeCRI, mergeCRI, mergeCRI)

        repo.record(doc.serialize()) # Record the provenance document.
        repo.logout()

        return doc

mergeAllWithoutDrugCrimes.execute()
doc = mergeAllWithoutDrugCrimes.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


# In[ ]:



