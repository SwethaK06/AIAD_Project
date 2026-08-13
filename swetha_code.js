const API_URL = "https://grown-surge-prince-agreement.trycloudflare.com/api/v1/optimize-route";
// the API url is the temporary backend endpoint. so each time we need to shut down or reopen, we need to change the url to the new one.
async function getOptimizedRoute(userInputs) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origin: {
          lat: userInputs.originLat,
          lng: userInputs.originLng,
          address: userInputs.originAddress
        },
        destination: {
          lat: userInputs.destLat,
          lng: userInputs.destLng,
          address: userInputs.destAddress
        },
        cargo_weight_kg: parseFloat(userInputs.weightKg),
        vehicle_type: userInputs.vehicleType,
        priority_weight: userInputs.priorityPreference
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Optimized Route Data:", data);
    return data;

  } catch (error) {
    console.error("Error fetching route from backend:", error);
  }
}