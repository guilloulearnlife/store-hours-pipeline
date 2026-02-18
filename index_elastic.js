import fs from "fs";
import path from "path";
import { Client } from "@elastic/elasticsearch";

const ES_NODE = process.env.ES_NODE || "http://host.docker.internal:9200";

const client = new Client({ node: ES_NODE });

function getIndexName(scrapeTs) {
  const d = new Date(scrapeTs);
  const yyyy = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `stores-hours-${yyyy}.${mm}.${dd}`;
}

async function run() {
  const processedDir = "./data/processed";
  const files = fs.readdirSync(processedDir)
    .filter(f => f.startsWith("stores_"))
    .sort();

  if (!files.length) {
    console.error("Keine stores_*.json in", processedDir);
    process.exit(1);
  }

  const latest = files[files.length - 1];
  const fullPath = path.join(processedDir, latest);
  const docs = JSON.parse(fs.readFileSync(fullPath, "utf8"));

  if (!docs.length) {
    console.error("Keine Dokumente in", fullPath);
    process.exit(1);
  }

  const scrapeTs = docs[0].scrape_timestamp || new Date().toISOString();
  const indexName = getIndexName(scrapeTs);

  const body = [];
  for (const doc of docs) {
    body.push({ index: { _index: indexName } });
    body.push(doc);
  }

  console.log(`Indexiere ${docs.length} Dokumente nach ${indexName} ...`);

  const res = await client.bulk({ body, refresh: true });
  const responseBody = res.body || res;

  if (responseBody.errors) {
    const failed = responseBody.items
      .filter(i => Object.values(i)[0].error)
      .slice(0, 5);
    console.error("Bulk-Fehler (erste 5):", JSON.stringify(failed, null, 2));
  } else {
    console.log("Bulk okay");
  }
}

run().catch(err => {
  console.error("Fehler beim Indexieren:", err);
  process.exit(1);
});
