#!/usr/bin/env node

const fs = require('fs')
const fetch = require('fetch-timeout')
const ipfsClient = require('ipfs-http-client')
const MongoClient = require('mongodb').MongoClient

const ipfsUpload = async (ipfs, data) => {
  let json = JSON.stringify(data)
  let content = Buffer.from(json)
  resp = await ipfs.add(content, { pin: false })
  return resp[0].hash
}

const updateDapp = async (dbCol, legacyHash, newHash) => {
  return dbCol.updateOne(
    {hash: legacyHash},
    {'$set': {ipfsHash: newHash}}
  )
}

const main = async () => {
  const mongo = await MongoClient.connect(
    process.env.MONGODB_URI,
    { useUnifiedTopology: true }
  )
  const db = mongo.db()
  const dbDapps = db.collection('dappsmetadatas')

  const ipfs = ipfsClient(
      process.env.IPFS_HOST || 'ipfs.status.im',
      process.env.IPFS_PORT || 443,
      { protocol: 'https' }
  )

  const dapps = await dbDapps.find().toArray()

  for (let dapp of dapps) {
    let legacyHash = dapp.hash
    let oldHash = dapp.ipfsHash
    console.log(` * ${dapp.details.name} - ${dapp.details.url}`)
    console.log(`   - LEG HASH: ${legacyHash}`)
    console.log(`   - OLD HASH: ${oldHash}`)
    let newHash = await ipfsUpload(ipfs, dapp.details)
    console.log(`   - NEW HASH: ${newHash}`)
    if (oldHash == newHash) {
      console.log('   - MATCHING')
      continue
    }

    let rval = await updateDapp(dbDapps, legacyHash, newHash)
    if (rval.result.ok != 1) {
      console.log('   ! FAILURE')
    }
    console.log('   ! UPDATED')
  }

  await mongo.close()
}

main()
