const handleSubmit = async (event) => {
  event.preventDefault();

  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());

  try {
    const res = await fetch("/items", {
      method: "POST",
      body,
    });
    const jsonRes = await res.json();
    if (jsonRes == "200") window.location.pathname = "/";
  } catch (e) {
    console.error(e);
  }
};

const form = document.querySelector("#write-form");
form.addEventListener("submit", handleSubmit);
