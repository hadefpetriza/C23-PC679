const findMyState = () => {
  const status = document.querySelector(".status");

  const success = (position) => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const keyword = status.innerHTML;

    const geoApiUrl = `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${lat},${lng}&radius=1500&type=landfills&keyword=${keyword}&key=AIzaSyDBHKAJ2094DScsRYyO1gdf5SBfsJUopzA`;

    fetch(geoApiUrl)
      .then((res) => res.json())
      .then((data) => {
        status.textContent = JSON.stringify(data);
        const results = data.results;
        if (results.length > 0) {
          const place = results[0];
          const placeLat = place.geometry.location.lat;
          const placeLng = place.geometry.location.lng;

          // Generate the Google Maps URL for the first place
          const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${placeLat},${placeLng}`;
          const mapLink = document.getElementById("map-link");
          mapLink.href = mapsUrl;
        }
      })
      .catch((error) => {
        console.log(error);
        status.textContent = "Error fetching data from API";
      });
  };

  const error = () => {
    status.textContent = "Lokasi tidak dapat ditemukan";
  };

  navigator.geolocation.getCurrentPosition(success, error);
};

document.querySelector(".find-state").addEventListener("click", findMyState);
