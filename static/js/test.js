async function readFiles(files) {
    // Make array from files, which is a FileList object. With .map(), return a new array where, for each file in files, 
    // returns a result of a Promise.
    var promises = Array.from(files).map((file) => {
        // .readAsDataURL() is an async method. A Promise is used to wait for its results.
        return new Promise((resolve, reject) => {
            reader = new FileReader();
            // .onload is a callback function that triggers when .readAsDataURL() successfully finishes.
            // It resolves the promise with the result of .readAsDataURL() and it is placed at its respective index
            // in the array returned by .map().
            reader.onload = (readerEvent) => {
                resolve(readerEvent.target.result);
            }
            reader.onerror = (error) => {
                reject(error);
            }
            reader.readAsDataURL(file);
        });
    });

    // results waits for all Promises in promises to resolve. It is then returned as an array of usable images.
    var results = await Promise.all(promises);
    console.log(`results ${results.length}`);
    return results;
}

$("#image-upload-input").change(async (elementEvent) => {
    var files = elementEvent.target.files;

    if (files) {
        // read all files, place in imageArray
        var imageArray = await readFiles(files);

        // append images in image array into #image-thumbnails element in page
        $('#image-thumbnail').attr('src', imageArray[0]);
        imageArray.forEach((image) => {
            $('#image-choices').append(`<img class="m-2 img-thumbnail" src="${image}" 
                style="width: 4rem; height: 4rem; object-fit: cover;">`);
        });
        $('#thumbnail-text').show();
    }
});

/*
        for (var i = 0; i < input.files.length; i++) {
            reader.onload = (readerEvent) => {
                imageArray.push(readerEvent.target.result);
                $('#image-preview').attr('src', imageArray[0]);

                if (i == input.files.length) {
                }
            };

            reader.readAsDataURL(input.files[i]);
            reader = new FileReader();
        }
        console.log(imageArray.length);
*/