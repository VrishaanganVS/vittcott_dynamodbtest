// backend/server.js (ESM) - CLEAN + FIXED OPTIONS HANDLING
import express from "express";
import dotenv from "dotenv";
dotenv.config();

import cors from "cors";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand, PutCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";
import bcrypt from "bcryptjs";
import { v4 as uuidv4 } from "uuid";
import jwt from "jsonwebtoken";

import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const app = express();
app.use(express.json());

// --- CORS setup ---
const rawOrigins = process.env.FRONTEND_ORIGINS || "http://localhost:8000";
const allowedOrigins = rawOrigins.split(",").map(s => s.trim()).filter(Boolean);
console.log("Allowed frontend origins:", allowedOrigins);

const corsOptions = {
  origin: (origin, callback) => {
    if (!origin) return callback(null, true); // allow curl/Postman
    if (allowedOrigins.includes(origin)) return callback(null, true);
    console.warn("❌ CORS blocked for origin:", origin);
    return callback(new Error("Not allowed by CORS"), false);
  },
  credentials: true,
  methods: ["GET","POST","PUT","DELETE","OPTIONS"],
  allowedHeaders: ["Authorization","Content-Type","X-Requested-With","Accept","Origin"]
};

// Apply cors
app.use(cors(corsOptions));


// --- SAFE OPTIONS HANDLER (fixes your error!) ---
app.use((req, res, next) => {
  if (req.method !== "OPTIONS") return next();

  const origin = req.headers.origin;
  if (origin && allowedOrigins.includes(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
  }

  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Authorization,Content-Type,X-Requested-With,Accept,Origin");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  return res.sendStatus(204);
});


// --- Logger to verify incoming requests ---
app.use((req, res, next) => {
  console.log(`➡️  Incoming request: ${req.method} ${req.url} (Origin: ${req.headers.origin || "N/A"})`);
  next();
});


// ENV
const REGION = process.env.AWS_REGION || "ap-south-1";
const USERS_TABLE = process.env.USERS_TABLE || "Vittcott_Users";
const JWT_SECRET = process.env.JWT_SECRET || "dev-secret";
const DYNAMODB_ENDPOINT = process.env.DYNAMODB_ENDPOINT || undefined;
const S3_BUCKET = process.env.S3_BUCKET || "vittcott-uploads-xyz123";

console.log("AWS Region:", REGION, "Users table:", USERS_TABLE, "S3 bucket:", S3_BUCKET);

// DynamoDB client
const ddbClientOpts = { region: REGION };
if (DYNAMODB_ENDPOINT) ddbClientOpts.endpoint = DYNAMODB_ENDPOINT;
const ddbClient = new DynamoDBClient(ddbClientOpts);
const ddb = DynamoDBDocumentClient.from(ddbClient);

// S3 client
const s3Client = new S3Client({ region: REGION });


// Helper: find user by email
async function getUserByEmail(email) {
  const normalized = email.trim().toLowerCase();
  const params = {
    TableName: USERS_TABLE,
    IndexName: "GSI_Email",
    KeyConditionExpression: "email = :e",
    ExpressionAttributeValues: { ":e": normalized },
    Limit: 1
  };
  const res = await ddb.send(new QueryCommand(params));
  return res.Count > 0 ? res.Items[0] : null;
}


// --- ROUTES ---

app.get("/", (req, res) => res.json({ ok: true }));


// REGISTER
app.post("/register", async (req, res) => {
  try {
    console.log("REGISTER BODY:", req.body);

    const { email, password, displayName } = req.body;
    if (!email || !password) return res.status(400).json({ error: "email and password required" });

    const normalized = email.toLowerCase().trim();
    const existing = await getUserByEmail(normalized);
    if (existing) return res.status(409).json({ error: "email already in use" });

    const hashed = await bcrypt.hash(password, 10);
    const userId = uuidv4();
    const now = new Date().toISOString();

    const item = {
      pk: `USER#${userId}`,
      userId,
      email: normalized,
      hashedPassword: hashed,
      displayName: displayName || null,
      createdAt: now,
      isEmailVerified: false,
      s3Keys: []
    };

    await ddb.send(new PutCommand({ TableName: USERS_TABLE, Item: item }));
    console.log("User created:", userId);

    return res.status(201).json({ message: "registered", userId });
  } catch (err) {
    console.error("Register error:", err);
    return res.status(500).json({ error: "internal", detail: err.message });
  }
});


// LOGIN
app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: "email and password required" });

    const user = await getUserByEmail(email);
    if (!user) return res.status(401).json({ error: "invalid credentials" });

    const ok = await bcrypt.compare(password, user.hashedPassword);
    if (!ok) return res.status(401).json({ error: "invalid credentials" });

    const token = jwt.sign({ userId: user.userId, email: user.email }, JWT_SECRET, { expiresIn: "1h" });

    return res.json({ token });
  } catch (err) {
    console.error("Login error:", err);
    return res.status(500).json({ error: "internal" });
  }
});


// Protected /me
app.get("/me", async (req, res) => {
  try {
    const authHeader = req.headers.authorization || "";
    const token = authHeader.split(" ")[1];
    if (!token) return res.status(401).json({ error: "no token" });

    const payload = jwt.verify(token, JWT_SECRET);
    const pk = `USER#${payload.userId}`;

    const result = await ddb.send(new QueryCommand({
      TableName: USERS_TABLE,
      KeyConditionExpression: "pk = :p",
      ExpressionAttributeValues: { ":p": pk },
      Limit: 1
    }));

    if (!result.Count) return res.status(404).json({ error: "not found" });

    const item = result.Items[0];
    delete item.hashedPassword;

    return res.json({ user: item });
  } catch (err) {
    console.error("/me error:", err);
    return res.status(500).json({ error: "internal" });
  }
});


// --- START SERVER ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log(`🔥 Server running on http://localhost:${PORT}`)
);
