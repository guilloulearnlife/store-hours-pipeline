import fs from "fs";
import path from "path";
import opening_hours from "opening_hours";

function parseOpeningHours(raw) {
  if (!raw) return { ok: false, error: "missing" };
  try {
    const oh = new opening_hours(raw);
    const weekday_hours = oh.getOpenIntervals(
      new Date("2025-01-06T00:00:00Z"),
      new Date("2025-01-13T00:00:00Z")
    );
    return { ok: true, weekday_hours };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

function normalizeElement(el, scrapeTs) {
  const tags = el.tags || {};
  const id = `${el.type}/${el.id}`;
  const addr = {
    street: tags["addr:street"] || null,
    city: tags["addr:city"] || null,
    postcode: tags["addr:postcode"] || null,
    country: tags["addr:country"] || null
  };

  const category =
    tags.shop === "supermarket" ? "supermarket" :
    tags.amenity === "pharmacy" ? "pharmacy" :
    "other";

    const oh = parseOpeningHours(tags.opening_hours);

    const doc = {
      source_id: id,
      category,
      name: tags.name || null,
      ...addr,
      website: tags.website || null,
      opening_hours_raw: tags.opening_hours || null,
      opening_hours_parse_ok: oh.ok,
      opening_hours_parse_error: oh.ok ? null : oh.error,
      scrape_timestamp: scrapeTs
    };
    
    if (oh.ok) {
      doc.opening_hours_parsed = JSON.stringify(oh.weekday_hours);
    }
    
    return doc;
        
  
}

function runOnce(filePath) {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  
  // NEU: Timestamp aus dem raw-Objekt holen
  const scrapeTs = raw.scrape_timestamp || new Date().toISOString();
  
  const elements = raw.elements || [];

  const normalized = elements.map(el => normalizeElement(el, scrapeTs));

  fs.mkdirSync("./data/processed", { recursive: true });
  const outName = path.basename(filePath).replace("overpass_", "stores_");
  fs.writeFileSync(
    `./data/processed/${outName}`,
    JSON.stringify(normalized, null, 2)
  );
  console.log("Normalized:", normalized.length, "records");
}

const latest = fs.readdirSync("./data/raw")
  .filter(f => f.startsWith("overpass_"))
  .sort()
  .pop();

runOnce(`./data/raw/${latest}`);
