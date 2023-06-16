function initMap() {
  const map = document.querySelector(".map");

  const success = (position) => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const search = document.getElementById("maps_keyword");
    const search_word = search.textContent;

    // Set the initial map location
    var center = { lat: lat, lng: lng }; // San Francisco coordinates

    // Create a new map instance
    var map = new google.maps.Map(document.getElementById("map"), {
      center: center,
      zoom: 15,
    });

    // Perform a nearby search
    var request = {
      location: center,
      radius: "5000", // Define the search radius in meters
      type: ["TPA"], // Specify the type of place you want to search for
      keyword: search_word,
    };

    var service = new google.maps.places.PlacesService(map);
    function createMarker(place) {
      var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        title: place.name,
        desc: place.photos,
      });

      var content =
        "<strong>" +
        place.name +
        "</strong><br>" +
        "Address: " +
        place.formatted_address +
        "<br>" +
        "Rating: " +
        place.rating;

      var infowindow = new google.maps.InfoWindow({
        content: content,
      });

      // Add a click event listener to the marker
      marker.addListener("click", function () {
        infowindow.open(map, marker); // Open the InfoWindow when marker is clicked
      });
    }

    service.nearbySearch(request, function (results, status) {
      if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
          createMarker(results[i]);
        }
      }
    });
  };

  const error = () => {
    map.textContent = "Lokasi tidak dapat ditemukan";
  };

  navigator.geolocation.getCurrentPosition(success, error);
}
