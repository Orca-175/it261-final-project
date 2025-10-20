async function readFiles(files) {
    // Make array from files, which is a FileList object. With .map(), return a new array where, for each file in files, 
    // returns a result of a Promise.
    var promises = Array.from(files).map((file) => {
        // .readAsDataURL() is an async method. A Promise is used to wait for its results.
        // Return reuslt of a Promise for each file in files.
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
            
            if (!file.type.startsWith('image/')) {
                reject('Non-image file detected. Please ensure that all uploads are image files.');
            } else {
                reader.readAsDataURL(file);
            }
        });
    });

    // results waits for all Promises in promises to resolve. It is then returned as an array of usable images.
    var results = await Promise.all(promises);
    return results;
}

function setThumbnail({imageArray, index} = {}) {
    if (Array.isArray(imageArray)) {
        setThumbnail.array = imageArray;
    }

    $('#product-thumbnail').attr('src', setThumbnail.array[index]);
}

$("#image-upload-input").change(async (elementEvent) => {
    var files = elementEvent.target.files;

    if (files) {
        // read all files, place in imageArray
        try {
            $('#image-choices').html('');
            $('#thumbnail-error').html('');
            $('#product-thumbnail').attr('src', '');

            var imageArray = await readFiles(files);

            // append images in image array into #image-thumbnails element in page
            setThumbnail({imageArray: imageArray, index: 0});
            imageArray.forEach((image, index) => {
                $('#image-choices').append(`<img id="${index}" class="m-2 img-thumbnail image-choice" src="${image}" 
                    style="width: 4rem; height: 4rem; object-fit: cover;">`);
            });
            $('#thumbnail-text').show();
        } catch (rejection) {
            $('#thumbnail-error').append(`<em class="text-center"">${rejection}</em>`);
            $('#thumbnail-text').hide();
        }
    }
});

$("#image-choices").on('click', '.image-choice', function() {
    var id = $(this).attr('id');
    $("#thumbnail-index").val(id);
    setThumbnail({index: id});
});