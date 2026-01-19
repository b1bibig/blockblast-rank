import { useMemo } from 'react';
import Hashing from './hashing';

export { Hashing };

export function HashBeacon({
  baseUrl,
  username,
  score,
  salt,
  timeStr,
  length = 16,
  hidden = true,
}) {
  const hash = useMemo(
    () => Hashing.makeHash({ timeStr, username, score, salt, length }),
    [timeStr, username, score, salt, length]
  );

  const src = useMemo(
    () => `${baseUrl}/${username}/${score}/${hash}?t=${Date.now()}`,
    [baseUrl, username, score, hash]
  );

  const style = hidden ? { display: 'none' } : undefined;

  return <img alt="score-beacon" src={src} style={style} />;
}
