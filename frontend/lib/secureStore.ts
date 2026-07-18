const KEY_NAME = "nimrod_groq_key_ciphertext";
const MATERIAL_NAME = "nimrod_local_crypto_material";

function bytesToBase64(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes));
}

function base64ToBytes(value: string): Uint8Array {
  return Uint8Array.from(atob(value), (char) => char.charCodeAt(0));
}

async function getLocalKey(): Promise<CryptoKey> {
  let material = localStorage.getItem(MATERIAL_NAME);
  if (!material) {
    const random = crypto.getRandomValues(new Uint8Array(32));
    material = bytesToBase64(random);
    localStorage.setItem(MATERIAL_NAME, material);
  }
  return crypto.subtle.importKey("raw", base64ToBytes(material), "AES-GCM", false, ["encrypt", "decrypt"]);
}

export async function saveGroqKey(apiKey: string): Promise<void> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const cipher = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await getLocalKey(), new TextEncoder().encode(apiKey));
  localStorage.setItem(KEY_NAME, JSON.stringify({ iv: bytesToBase64(iv), cipher: bytesToBase64(new Uint8Array(cipher)) }));
}

export async function getGroqKey(): Promise<string | null> {
  const stored = localStorage.getItem(KEY_NAME);
  if (!stored) return null;
  try {
    const parsed = JSON.parse(stored) as { iv: string; cipher: string };
    const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: base64ToBytes(parsed.iv) }, await getLocalKey(), base64ToBytes(parsed.cipher));
    return new TextDecoder().decode(plain);
  } catch {
    localStorage.removeItem(KEY_NAME);
    return null;
  }
}
