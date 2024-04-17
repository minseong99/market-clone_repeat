const form = document.querySelector("#login-form");
let accessToken = null;
const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const sha256Password = sha256(formData.get("password"));
  formData.set("password", sha256Password);

  const res = await fetch("/login", {
    method: "POST",
    body: formData,
  });

  // res.status : 상태 코드를 내려준다.
  const data = await res.json();

  if (res.status === 200) {
    accessToken = data.access_token;
    refreshToken = data.refresh_token;
    window.localStorage.setItem("access_token", accessToken);
    window.localStorage.setItem("refresh_token", refreshToken);
    alert("로그인에 성공했습니다.");

    window.location.pathname = "/";
  } else if (res.status === 401) {
    alert("아이디 혹은 비밀번호가 틀렸습니다");
  }
};

form.addEventListener("submit", handleSubmit);
