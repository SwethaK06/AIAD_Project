const NOMINATIM_URL =
  "https://nominatim.openstreetmap.org/search";

export async function geocodeSingaporeAddress(address) {
  const params = new URLSearchParams({
    q: `${address}, Singapore`,
    format: "jsonv2",
    limit: "5",
    countrycodes: "sg",
    addressdetails: "1",
    layer: "address,poi",
  });

  const response = await fetch(
    `${NOMINATIM_URL}?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(
      "Unable to contact the geocoding service."
    );
  }

  const results = await response.json();

  if (!results || results.length === 0) {
    throw new Error(
      `Could not find a Singapore location for "${address}".`
    );
  }

  return results.map((result) => ({
    lat: Number(result.lat),
    lng: Number(result.lon),
    address: result.display_name,
    osmId: result.osm_id,
    osmType: result.osm_type,
  }));
}