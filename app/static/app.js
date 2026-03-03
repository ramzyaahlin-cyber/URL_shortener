const form = document.getElementById('shorten-form');
const message = document.getElementById('message');
const result = document.getElementById('result');
const shortUrlEl = document.getElementById('short-url');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const url = document.getElementById('url').value.trim();

  message.textContent = 'Creating short URL...';
  result.classList.add('hidden');

  const payload = { url };

  try {
    const response = await fetch('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      message.textContent = data.detail || 'Failed to shorten URL';
      return;
    }

    shortUrlEl.href = data.short_url;
    shortUrlEl.textContent = data.short_url;

    result.classList.remove('hidden');
    message.textContent = 'Short URL created successfully.';
  } catch (error) {
    message.textContent = 'Server error. Please try again.';
  }
});
