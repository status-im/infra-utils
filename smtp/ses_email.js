#!/usr/bin/env node

const nodemailer = require('nodemailer')

const SMTP_CONF = {
    host: 'email-smtp.us-east-1.amazonaws.com',
    port: 465,
    secure: process.env.SMTP_TLS,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
    },
}

const EMAIL = {
  from: 'Dapps Approvals <dapps-approvals@dap.ps>',
  to: 'dapps-approvals@status.im',
  subject: 'Test Email', 
  text: 'Test email from status-im/infra-utils/blob/master/smtp/ses_email.js',
}

async function main() {
  let rval
  let smtp = nodemailer.createTransport(SMTP_CONF)

  console.log('Sending:')
  console.dir(EMAIL)

  try {
    await smtp.verify()
    rval = await smtp.sendMail(EMAIL)
  } catch (e) {
    console.error(`Email delivery failed: ${e}`)
    return
  }

  console.log('Response:')
  console.dir(rval)
  console.log(`Email delivered successfully!`)
}

main()
