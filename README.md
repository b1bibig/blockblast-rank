# Blockblast Rank

## JSX 컴포넌트

```jsx
function HashBeacon({
  baseUrl,
  username,
  score,
  salt,
  timeStr,
  length = 16,
  hidden = true,
}) {
  const hash = Hashing.makeHash({ timeStr, username, score, salt, length });
  const src = `${baseUrl}/${username}/${score}/${hash}?t=${Date.now()}`;

  return <img alt="score-beacon" src={src} style={hidden ? { display: 'none' } : undefined} />;
}
```

```jsx
const Hashing = {
  makeHashInput({ timeStr, username, score, salt }) {
    const [ampm, hm] = timeStr.split(' ');
    const [hour, minute] = hm.split(':');
    const mm = minute.padStart(2, '0');
    return `${ampm}${hour}:${mm}:${username}:${score}:${salt}`;
  },
  base64Utf8(value) {
    const bytes = new TextEncoder().encode(value);
    let binary = '';
    bytes.forEach((byte) => {
      binary += String.fromCharCode(byte);
    });
    return btoa(binary);
  },
  makeHash({ timeStr, username, score, salt, length = 16 }) {
    const input = Hashing.makeHashInput({ timeStr, username, score, salt });
    const full = Hashing.base64Utf8(input);
    return full.slice(0, length);
  },
};
```
