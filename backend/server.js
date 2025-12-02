// backend/server.js (ESM) - CLEAN + FIXED OPTIONS HANDLING
import express from "express";
import dotenv from "dotenv";
dotenv.config();

import cors from "cors";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand, PutCommand, ScanCommand } from "@aws-sdk/lib-dynamodb";
import bcrypt from "bcryptjs";
import { v4 as uuidv4 } from "uuid";
import jwt from "jsonwebtoken";

import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import fs from 'fs';
import path from 'path';
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const app = express();
app.use(express.json());

// --- CORS setup ---
const rawOrigins = process.env.FRONTEND_ORIGINS || "http://localhost:3000,http://localhost:5173,http://localhost:8000";
const allowedOrigins = rawOrigins.split(",").map(s => s.trim()).filter(Boolean);
console.log("Allowed frontend origins:", allowedOrigins);

const corsOptions = {
  origin: (origin, callback) => {
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes(origin)) return callback(null, true);
    console.warn("❌ CORS blocked for origin:", origin);
    return callback(new Error("Not allowed by CORS"), false);
  },
  credentials: true,
  methods: ["GET","POST","PUT","DELETE","OPTIONS"],
  allowedHeaders: ["Authorization","Content-Type","X-Requested-With","Accept","Origin"]
};

app.use(cors(corsOptions));

// --- SAFE OPTIONS HANDLER ---
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

// --- Logger ---
app.use((req, res, next) => {
  console.log(`➡️  ${req.method} ${req.url} (Origin: ${req.headers.origin || "N/A"})`);
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

// --- Optional: auto-create DynamoDB table in dev/local setups ---
const AUTO_CREATE_TABLE = (process.env.AUTO_CREATE_TABLE === 'true');
const SHOULD_AUTO_CREATE = AUTO_CREATE_TABLE || (DYNAMODB_ENDPOINT && DYNAMODB_ENDPOINT.includes('localhost'));

if (SHOULD_AUTO_CREATE) {
  (async () => {
    try {
      console.log('⏳ AUTO_CREATE_TABLE is enabled — attempting to create users table if needed');
      const mod = await import('./create_table.js');
      if (mod && typeof mod.createTable === 'function') {
        await mod.createTable();
      }
    } catch (err) {
      console.warn('⚠️ Auto-create table failed:', err && err.message ? err.message : err);
    }
  })();
}

// Helper: find user by email using GSI
async function getUserByEmail(email) {
  const normalized = email.trim().toLowerCase();
  const params = {
    TableName: USERS_TABLE,
    IndexName: "GSI_Email",
    KeyConditionExpression: "email = :e",
    ExpressionAttributeValues: { ":e": normalized },
    Limit: 1
  };
  try {
    const res = await ddb.send(new QueryCommand(params));
    return res.Count > 0 ? res.Items[0] : null;
  } catch (err) {
    console.warn("⚠️  DynamoDB query error (getUserByEmail):", err.message || err);
    // Fallback: scan if GSI doesn't exist yet (slower but works)
    try {
      const scanParams = {
        TableName: USERS_TABLE,
        FilterExpression: "email = :e",
        ExpressionAttributeValues: { ":e": normalized },
        Limit: 1
      };
      const scanRes = await ddb.send(new ScanCommand(scanParams));
      return scanRes.Count > 0 ? scanRes.Items[0] : null;
    } catch (scanErr) {
      console.warn("⚠️  Scan also failed:", scanErr.message);
      return null;
    }
  }
}

// --- ROUTES ---

app.get("/", (req, res) => res.json({ ok: true, message: "VittCott Backend Running!" }));

// Serve frontend static files (if copied into backend/src/frontend_build)
try {
  const STATIC_DIR = path.join(process.cwd(), 'src', 'frontend_build');
  if (fs.existsSync(STATIC_DIR)) {
    console.log('📦 Serving static frontend from', STATIC_DIR);
    app.use(express.static(STATIC_DIR));
  }
} catch (err) {
  console.warn('Could not set up static frontend serving:', err && err.message ? err.message : err);
}

// REGISTER (Signup)
app.post("/register", async (req, res) => {
  try {
    console.log("📝 REGISTER REQUEST:", req.body);

    const { email, password, displayName } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: "email and password required" });
    }

    const normalized = email.toLowerCase().trim();
    
    // Check if email already exists
    const existing = await getUserByEmail(normalized);
    if (existing) {
      console.log("⚠️  Email already exists:", normalized);
      return res.status(409).json({ error: "email already in use" });
    }

    // Hash password
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

    try {
      await ddb.send(new PutCommand({ TableName: USERS_TABLE, Item: item }));
      console.log("✅ User created in DynamoDB:", userId, normalized);
    } catch (err) {
      console.error("❌ DynamoDB put error:", err);
      return res.status(500).json({ error: "database error", detail: err.message });
    }

    return res.status(201).json({ 
      message: "registered successfully", 
      userId,
      email: normalized 
    });
  } catch (err) {
    console.error("❌ Register error:", err);
    return res.status(500).json({ error: "internal server error", detail: err.message });
  }
});

// LOGIN
app.post("/login", async (req, res) => {
  try {
    console.log("🔑 LOGIN REQUEST:", { email: req.body.email });

    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: "email and password required" });
    }

    const user = await getUserByEmail(email);
    if (!user) {
      console.log("⚠️  User not found:", email);
      return res.status(401).json({ error: "invalid credentials" });
    }

    const ok = await bcrypt.compare(password, user.hashedPassword);
    if (!ok) {
      console.log("⚠️  Invalid password for:", email);
      return res.status(401).json({ error: "invalid credentials" });
    }

    const token = jwt.sign(
      { userId: user.userId, email: user.email }, 
      JWT_SECRET, 
      { expiresIn: "7d" }
    );

    console.log("✅ Login successful:", user.email);

    return res.json({ 
      token,
      user: {
        userId: user.userId,
        email: user.email,
        displayName: user.displayName || email.split('@')[0]
      }
    });
  } catch (err) {
    console.error("❌ Login error:", err);
    return res.status(500).json({ error: "internal server error" });
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

    if (!result.Count) return res.status(404).json({ error: "user not found" });

    const item = result.Items[0];
    delete item.hashedPassword;

    return res.json({ user: item });
  } catch (err) {
    console.error("❌ /me error:", err);
    return res.status(401).json({ error: "invalid token" });
  }
});

// --- START SERVER ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log(`🔥 VittCott Backend running on http://localhost:${PORT}`)
);