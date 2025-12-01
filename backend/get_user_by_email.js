#!/usr/bin/env node
import dotenv from 'dotenv';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';

dotenv.config();

const REGION = process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || 'ap-south-1';
const DDB_ENDPOINT = process.env.DYNAMODB_ENDPOINT || undefined;
const USERS_TABLE = process.env.USERS_TABLE || 'Vittcott_Users';

const email = process.argv[2];
if (!email) {
  console.error('Usage: node get_user_by_email.js <email>');
  process.exit(2);
}

const clientOpts = { region: REGION };
if (DDB_ENDPOINT) clientOpts.endpoint = DDB_ENDPOINT;

const client = new DynamoDBClient(clientOpts);
const ddb = DynamoDBDocumentClient.from(client);

async function run() {
  try {
    const params = {
      TableName: USERS_TABLE,
      IndexName: 'GSI_Email',
      KeyConditionExpression: 'email = :e',
      ExpressionAttributeValues: { ':e': email }
    };
    const res = await ddb.send(new QueryCommand(params));
    console.log('Query result count:', res.Count || 0);
    if (res.Items && res.Items.length) {
      console.log('First item:', JSON.stringify(res.Items[0], null, 2));
    } else {
      console.log('No items found for email', email);
    }
  } catch (err) {
    console.error('Query failed:', err && err.message ? err.message : err);
    process.exit(3);
  }
}

run();
