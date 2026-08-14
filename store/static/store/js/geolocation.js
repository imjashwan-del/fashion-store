/*
 * Captures the customer's REAL device coordinates via the browser's
 * HTML5 Geolocation API and fills the hidden latitude/longitude fields
 * on the checkout form before it can be submitted for online delivery.
 *
 * Why this exists (see store/utils.py for the full rationale): the
 * project intentionally does NOT infer delivery distance from a typed
 * address or PIN code, because that can't be trusted as accurate. This
 * is the one point in the flow where we get a real, verifiable
 * coordinate pair. The server (store/views.py:checkout) re-checks the
 * distance itself -- this script never decides eligibility, it only
 * supplies the real location for the server to check.
 */
document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('checkoutForm');
  if (!form) return;

  var latField = form.querySelector('input[name="latitude"]');
  var lngField = form.querySelector('input[name="longitude"]');
  var statusBox = document.getElementById('locationStatus');
  var submitBtn = document.getElementById('checkoutSubmit');

  function setStatus(text, state) {
    if (!statusBox) return;
    statusBox.textContent = text;
    statusBox.className = 'location-status' + (state ? ' ' + state : '');
  }

  function requestLocation() {
    if (!('geolocation' in navigator)) {
      setStatus('Your browser does not support location access. Please call the store to place an order.', 'error');
      if (submitBtn) submitBtn.disabled = true;
      return;
    }

    setStatus('Checking that we deliver to your location…');
    navigator.geolocation.getCurrentPosition(
      function (position) {
        latField.value = position.coords.latitude;
        lngField.value = position.coords.longitude;
        setStatus('Location verified. We can check delivery availability for your address.', 'ok');
        if (submitBtn) submitBtn.disabled = false;
      },
      function () {
        setStatus(
          "We couldn't access your location. Please allow location access in your browser " +
          'and refresh this page, or call the store directly to place your order.',
          'error'
        );
        if (submitBtn) submitBtn.disabled = true;
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  requestLocation();

  var retryBtn = document.getElementById('retryLocation');
  if (retryBtn) retryBtn.addEventListener('click', requestLocation);
});
