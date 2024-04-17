const handleSubmit = async (event) => {
  event.preventDefault();
  let accessToken = window.localStorage.getItem("access_token");
  const refreshToken = window.localStorage.getItem("refresh_token");
  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());

  try {
    const res = await fetch("/items", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body,
    });
    const jsonRes = await res.json();
    if (res.status === 401) {
      const res3 = await fetch("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      const data2 = await res3.json();
      accessToken = data2.access_token;
      window.localStorage.setItem("access_token", accessToken);
    }
    if (jsonRes == "200") window.location.pathname = "/";
  } catch (e) {
    console.error(e);
  }
};

const form = document.querySelector("#write-form");
form.addEventListener("submit", handleSubmit);
