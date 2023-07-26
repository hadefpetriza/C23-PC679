function initMap() {
  const map = document.querySelector(".map");

  const success = (position) => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const search = document.getElementById("maps_keyword");
    const filename = document.getElementById("filename");
    const file = filename.textContent;
    const search_word = search.textContent;
    // send it into flask
    const data = {
      latitude: lat,
      longitude: lng,
      keyword: search_word,
      file: file,
    };

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
      radius: "10000", // Define the search radius in meters
      type: ["sampah"], // Specify the type of place you want to search for
      keyword: search_word,
    };

    var service = new google.maps.places.PlacesService(map);
    function createMarker(place) {
      var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        title: place.name,
      });

      var content =
        "<strong>" +
        place.name +
        "</strong><br>" +
        '<a href="https://www.google.com/maps/place/?q=place_id:' +
        place.place_id +
        '" target="_blank">View on Google Maps</a></div>';

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
    map.textContent = "Please Turn On Your Location";
  };

  navigator.geolocation.getCurrentPosition(success, error);
}
