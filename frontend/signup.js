const checkPassword = () => {
  const formData = new FormData(form);
  const password = formData.get("password");
  const password2 = formData.get("password2");
  if (password === password2) return true;
};

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const sha256Password = sha256(formData.get("password"));
  formData.set("password", sha256Password);

  const div = document.querySelector("#info");
  if (checkPassword()) {
    const res = await fetch("/signup", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (data === "200") {
      // div.innerText = "회원가입에 성공했습니다.";
      // div.style.color = "blue";
      alert("회원가입이 완료되었습니다.");
      window.location.pathname = "/login.html";
    } else if (data === "401") {
      div.innerText = "아이디가 이미 존재합니다.";
      div.style.color = "red";
    }
  } else {
    div.innerText = "비밀번호가 같지 않습니다.";
    div.style.color = "red";
  }
};

const form = document.querySelector("#signup-form");
form.addEventListener("submit", handleSubmit);
