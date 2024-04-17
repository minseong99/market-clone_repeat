const setTime = (timeStamp) => {
  // write.js에서 시간을 저장할때 utc시간으로 저장됨
  // 여기서 계산할때는 한국시간 기준으로 계산됨
  // 한국시간 utc + 9
  const curTime = new Date().getTime() - 9 * 60 * 60 * 1000;
  const passedTime = new Date(curTime - timeStamp);
  const month = passedTime.getMonth();
  const date = passedTime.getDate();
  const hour = passedTime.getHours();
  const minute = passedTime.getMinutes();
  const second = passedTime.getSeconds();

  if (month > 1) return `${month}달 전`;
  else if (date > 1) return `${date}일 전`;
  else if (hour > 0) return `${hour}시간 전`;
  else if (minute > 0) return `${minute}분 전`;
  else if (second > 0) return `${second}초 전`;
  else return "방금 전";
};

const renderData = (jsonRes) => {
  const main = document.querySelector("main");

  // jsonRes배열에서 제일 나중에 저장된 값이 forEach문을 제일먼저 돌기 때문에
  // 맨밑에 오게된다. 때문에 reverse()를 사용하여 최근 등록된 데이터가
  // 맨 위에 보이도록 한다.
  jsonRes.reverse().forEach(async (obj) => {
    const divList = document.createElement("div");
    divList.className = "item-list";

    const divImg = document.createElement("div");
    divImg.className = "item-list__img";

    const img = document.createElement("img");
    // img 서버에 요청
    const res = await fetch(`/images/${obj.id}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    img.src = url;

    const divInfo = document.createElement("div");
    divInfo.className = "item-list__info";

    const divTitle = document.createElement("div");
    divTitle.className = "item-list__info-title";
    divTitle.innerText = obj.title;

    const divMeta = document.createElement("div");
    divMeta.className = "item-list__info-meta";
    const passedTime = setTime(obj.insertAt);
    divMeta.innerText = obj.place + " " + passedTime;

    const divPrice = document.createElement("div");
    divPrice.className = "item-list__info-price";
    divPrice.innerText = obj.price;

    divInfo.appendChild(divTitle);
    divInfo.appendChild(divMeta);
    divInfo.appendChild(divPrice);

    divImg.appendChild(img);
    divList.appendChild(divImg);
    divList.appendChild(divInfo);

    main.appendChild(divList);
  });
};

const fetchList = async () => {
  let accessToken = window.localStorage.getItem("access_token");
  const refreshToken = window.localStorage.getItem("refresh_token");

  //유효 검사

  const res = await fetch("/items", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
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
    window.location.pathname = "/";
  }

  renderData(jsonRes);
};

fetchList();
