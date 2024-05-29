// Tüm yorum öğelerini seç
var commentElements = document.querySelectorAll('.x1lliihq');

// Her yorum öğesini döngü ile gez
commentElements.forEach(function(commentElement, index) {
    // Kullanıcı adını al
    var username = document.querySelectorAll('._ap3a')[index].textContent.trim();

    // Paylaşım zamanını al
    var postTime = document.querySelectorAll('time')[index].getAttribute('datetime');

    // Yorumu al
    var commentText = commentElement.textContent.trim();

    // Bilgileri yazdır
    console.log("Kullanıcı adı: ", username);
    console.log("Paylaşım zamanı: ", postTime);
    console.log("Yorum: ", commentText);
});


////////////////////

var comments = document.querySelectorAll('.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1');
//x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1
//.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1

// comments içerisinde bulunan yorumları yazdır
comments.forEach(function(comment) {
    console.log(comment.innerText);
});
