#!/usr/bin/env node

const fs = require('fs')
const ipfsClient = require('ipfs-http-client')

const main = async () => {
  const ipfs = ipfsClient(
      process.env.IPFS_HOST,
      process.env.IPFS_PORT,
      { protocol: 'https' }
  )

  let imgData = fs.readFileSync('image.png.url', 'utf8')

  let content = imgData.split(',')[1]
  let data = {
    path: 'test.png',
    content: Buffer.from(content, 'base64'),
  }
  let resp = await ipfs.add(data.content, { pin: true })

  console.log(`https://${process.env.IPFS_HOST}/${resp[0].hash}`)
}

main()
