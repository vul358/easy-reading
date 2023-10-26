function readingTime(size) {
    let readingHours = Math.floor(size / 100 * 50 / 60);
    return `預估閱讀時間：約${readingHours}~${readingHours+1}小時`;
}


function bookMark(data) {
    const api = "/novels/mark/";
    fetch(api, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if(!response.ok){
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
}


function insertBooks(data, divID) {
    const booksContainer = document.getElementById(divID);
    booksContainer.innerHTML = ""; // Clear previous books
  
    for (let i = 0; i < data.length; i++) {
      const item = data[i];
      const bookDiv = document.createElement("div");
      bookDiv.className = "novel";
      bookDiv.setAttribute("novel_num", i); 

      const msg = document.createElement("div");
      if (item.message) {
        msg.className="alert alert-info col-8";
        msg.setAttribute("role", "alert");
        msg.textContent = item.message;
        booksContainer.appendChild(msg);
      } else {

      const bookName = document.createElement("div");
      bookName.className = "title";
      bookName.textContent = item.title;

      const bookYear = document.createElement("span");
      bookYear.className = "year";
      bookYear.textContent = item.date;

      const bookSize = document.createElement("span");
      bookSize.className = "size";
      bookSize.textContent = readingTime(item.size);

      const author = document.createElement("div");
      author.className = "author";
      author.textContent = item.author;

      const outline = document.createElement("div");
      outline.className = "outline";
      outline.textContent = item.outline;

      const cat = document.createElement("div");
      cat.className = "category";
      cat.textContent = item.category;

      const tags = document.createElement("div");
      tags.className = "tags";
      if (item.tags){
        tags.textContent = item.tags
      }
      
      const url = document.createElement("a");
      url.className = "url";
      url.href = item.url;
      url.target = "_blank";
      url.textContent = "前往閱讀";


      const icon = document.createElement("span");
      icon.className = "bi bi-star";
      icon.addEventListener("click", function(){
        icon.className = "bi bi-star-fill";
        iconRemove.className = "bi bi-x-circle";


        const data = {
            "user_id": user,
            "bookshelf": "pending",
            "title": item.title,
            "author": item.author,
            "outline": item.outline,
            "url": item.url,
            "category": item.category,
        };
        bookMark(data);          
      });

      const iconRemove = document.createElement("span");
      iconRemove.className = "bi bi-x-circle";
      iconRemove.addEventListener("click", function(){
        iconRemove.className = "bi bi-x-circle-fill";
        icon.className = "bi bi-star"

        const data = {
            "user_id": user,
            "bookshelf": "blocked",
            "title": item.title,
            "author": item.author,
            "outline": item.outline,
            "url": item.url,
            "category": item.category,
            "year": item.year
        };
        bookMark(data);  
      });

      bookDiv.appendChild(bookName);
      bookName.appendChild(bookYear);
      bookDiv.appendChild(author);
      author.appendChild(bookSize);
      bookDiv.appendChild(cat);
      bookDiv.appendChild(tags)
      bookDiv.appendChild(outline);
      bookDiv.appendChild(url);
      bookDiv.appendChild(icon);
      bookDiv.appendChild(iconRemove);
    
    booksContainer.appendChild(bookDiv);
  }
}}