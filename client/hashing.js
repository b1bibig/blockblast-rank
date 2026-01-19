const Hashing = (() => {
  const makeHashInput = ({ timeStr, username, score, salt }) => {
    const [ampm, hm] = timeStr.split(' ');
    const [hour, minute] = hm.split(':');
    const mm = minute.padStart(2, '0');
    return `${ampm}${hour}:${mm}:${username}:${score}:${salt}`;
  };

  const base64Utf8 = (value) => {
    const bytes = new TextEncoder().encode(value);
    let binary = '';
    bytes.forEach((byte) => {
      binary += String.fromCharCode(byte);
    });
    return btoa(binary);
  };

  const makeHash = ({ timeStr, username, score, salt, length = 16 }) => {
    const input = makeHashInput({ timeStr, username, score, salt });
    const full = base64Utf8(input);
    return full.slice(0, length);
  };

  return {
    makeHashInput,
    base64Utf8,
    makeHash,
  };
})();

export default Hashing;
