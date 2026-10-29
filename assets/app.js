const menuButton = document.querySelector(".menu-toggle");
const sidebar = document.querySelector(".sidebar");
const protectedCode = document.querySelector(".protected-code");

const decodeBase64 = (value) => Uint8Array.from(atob(value.replace(/-/g, "+").replace(/_/g, "/")), (character) => character.charCodeAt(0));

const decryptCode = async (payload, pin) => {
  const parsed = JSON.parse(new TextDecoder().decode(decodeBase64(payload)));
  const material = await crypto.subtle.importKey("raw", new TextEncoder().encode(pin), "PBKDF2", false, ["deriveBits"]);
  const keyBits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: decodeBase64(parsed.salt), iterations: parsed.iterations, hash: "SHA-256" },
    material,
    256,
  );
  const key = new Uint8Array(keyBits);
  const nonce = decodeBase64(parsed.nonce);
  const ciphertext = decodeBase64(parsed.ciphertext);
  const plaintext = new Uint8Array(ciphertext.length);
  for (let offset = 0, counter = 0; offset < ciphertext.length; offset += 32, counter += 1) {
    const counterBytes = new Uint8Array(4);
    new DataView(counterBytes.buffer).setUint32(0, counter);
    const streamInput = new Uint8Array(key.length + nonce.length + counterBytes.length);
    streamInput.set(key);
    streamInput.set(nonce, key.length);
    streamInput.set(counterBytes, key.length + nonce.length);
    const stream = new Uint8Array(await crypto.subtle.digest("SHA-256", streamInput));
    for (let index = 0; index < Math.min(32, ciphertext.length - offset); index += 1) {
      plaintext[offset + index] = ciphertext[offset + index] ^ stream[index];
    }
  }
  const checksum = new Uint8Array(await crypto.subtle.digest("SHA-256", plaintext));
  const expectedChecksum = decodeBase64(parsed.checksum);
  if (checksum.length !== expectedChecksum.length || checksum.some((value, index) => value !== expectedChecksum[index])) {
    throw new Error("Vale PIN");
  }
  return new TextDecoder().decode(plaintext);
};

const openCodePrompt = () => {
  if (!protectedCode || protectedCode.querySelector("pre")) return;
  const pin = window.prompt("Sisesta koodinäite PIN:");
  if (pin === null) return;
  decryptCode(protectedCode.dataset.codePayload, pin)
    .then((code) => {
      protectedCode.innerHTML = `${protectedCode.querySelector("h4").outerHTML}<pre><code class="language-cpp">${code}</code></pre>`;
      protectedCode.removeAttribute("hidden");
    })
    .catch(() => {
      window.alert("PIN ei sobi või koodinäidet ei saanud avada.");
    });
};

document.addEventListener("keydown", (event) => {
  if (event.key === "Tab" && protectedCode) {
    openCodePrompt();
  }
});

if (menuButton && sidebar) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    sidebar.classList.toggle("is-open", !expanded);
  });
}
