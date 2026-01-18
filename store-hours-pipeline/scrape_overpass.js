import fetch from "node-fetch";
import fs from "fs";

const OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter";

const QUERY = `
[out:json][timeout:60];
area["name"="Worms"]["boundary"="administrative"]->.searchArea;
(
  node["shop"="supermarket"]["opening_hours"](area.searchArea);
  way["shop"="supermarket"]["opening_hours"](area.searchArea);
  node["amenity"="pharmacy"]["opening_hours"](area.searchArea);
  way["amenity"="pharmacy"]["opening_hours"](area.searchArea);
);
out center tags;
`;

async function run() {
  const res = await fetch(OVERPASS_URL, {
    method: "POST",
    body: QUERY,
    headers: { "Content-Type": "text/plain" }
  });

  if (!res.ok) {
    throw new Error(`Overpass error: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  const ts = new Date().toISOString();
  
  // NEU: Timestamp direkt ins JSON speichern
  data.scrape_timestamp = ts;
  
  fs.mkdirSync("./data/raw", { recursive: true });
  fs.writeFileSync(`./data/raw/overpass_${ts.replace(/[:.]/g, "-")}.json`, JSON.stringify(data, null, 2));
  console.log("Saved:", `./data/raw/overpass_${ts.replace(/[:.]/g, "-")}.json`);
}

run().catch(console.error);

