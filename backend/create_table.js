#!/usr/bin/env node
import dotenv from 'dotenv';
import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

dotenv.config();

const REGION = process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || 'ap-south-1';
const DYNAMODB_ENDPOINT = process.env.DYNAMODB_ENDPOINT || process.env.DDB_ENDPOINT || undefined;
const USERS_TABLE = process.env.USERS_TABLE || 'Vittcott_Users';

console.log('Create table script');
console.log('Region:', REGION);
console.log('Endpoint:', DYNAMODB_ENDPOINT || '(aws)');
console.log('Table:', USERS_TABLE);

const clientOpts = { region: REGION };
if (DYNAMODB_ENDPOINT) clientOpts.endpoint = DYNAMODB_ENDPOINT;

const client = new DynamoDBClient(clientOpts);

async function createTable() {
  const params = {
    TableName: USERS_TABLE,
    AttributeDefinitions: [
      { AttributeName: 'pk', AttributeType: 'S' },
      { AttributeName: 'email', AttributeType: 'S' }
    ],
    KeySchema: [
      { AttributeName: 'pk', KeyType: 'HASH' }
    ],
    ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 },
    GlobalSecondaryIndexes: [
      {
        IndexName: 'GSI_Email',
        KeySchema: [ { AttributeName: 'email', KeyType: 'HASH' } ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
      }
    ]
  };

  try {
    const cmd = new CreateTableCommand(params);
    const res = await client.send(cmd);
    console.log('CreateTable response:', res.TableDescription.TableStatus);
    console.log('Table created successfully (or is being created).');
  } catch (err) {
    const msg = err && err.name ? `${err.name}: ${err.message}` : String(err);
    if (msg.includes('ResourceInUseException') || msg.includes('TableAlreadyExistsException')) {
      console.log('Table already exists.');
      process.exit(0);
    }
    console.error('Create table failed:', msg);
    process.exit(2);
  }
}
export { createTable };

// If run directly from CLI, execute
if (process.argv[1] && process.argv[1].endsWith('create_table.js')) {
  createTable();
}
