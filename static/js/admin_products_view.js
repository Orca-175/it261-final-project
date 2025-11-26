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

function setImageChoices(image, index) {
    $('#image-choices').append(`<img id='${index}' class='m-2 img-thumbnail image-choice' src='${image}' 
        style='width: 4rem; height: 4rem; object-fit: cover;'>`);
    $('#choose-thumbnail-text').show();
}

function initializeTooltips() {
    [...$('[data-bs-toggle="tooltip"')].forEach((tooltip) => {
        new bootstrap.Tooltip(tooltip);
    });
}

initializeTooltips();

$('#image-upload-input').on('change', async (elementEvent) => {
    var files = elementEvent.target.files;

    if (files) {
        // read all files, place in imageArray
        try {
            $('#image-choices').html('');
            $('#thumbnail-error-message').html('');
            $('#product-thumbnail').attr('src', '');

            var imageArray = await readFiles(files);

            // append images in image array into #image-thumbnails element in page
            setThumbnail({imageArray: imageArray, index: 0});
            imageArray.forEach((image, index) => {
                setImageChoices(image, index);
            });
        } catch (rejection) {
            $('#thumbnail-error-message').append(`<em class='text-center''>${rejection}</em>`);
            $('#choose-thumbnail-text').hide();
        }
    }
});

$('#image-choices').on('click', '.image-choice', function() {
    var id = $(this).attr('id');
    $('#thumbnail-index').val(id);
    setThumbnail({index: id});
});

$('#edit-form-btn').on('click', () => {
    $('#choose-thumbnail-text').hide();
    $('#image-choices').html('');
    $('#thumbnail-error-message').html('');
    $('#product-thumbnail').attr('src', staticPrefix + 'site-images/placeholder-image.png');
    $('#image-upload-input').val('');

    $('#product-form').attr('action', '/admin_edit_product');
    $('#add-form').hide();
    $('#add-form-btn').removeClass('active-text-color').addClass('inactive-text-color text-btn-hover');

    $('#edit-form').show();
    $('#edit-form-btn').removeClass('inactive-text-color text-btn-hover').addClass('active-text-color');
});

$('#add-form-btn').on('click', () => {
    $('#choose-thumbnail-text').hide();
    $('#image-choices').html('');
    $('#thumbnail-error-message').html('');
    $('#product-thumbnail').attr('src', staticPrefix + 'site-images/placeholder-image.png');
    $('#image-upload-input').val('');

    $('#product-form').attr('action', '/admin_add_product');
    $('#edit-form').hide();
    $('#edit-form-btn').removeClass('active-text-color').addClass('inactive-text-color text-btn-hover');

    $('#add-form').show();
    $('#add-form-btn').removeClass('inactive-text-color text-btn-hover').addClass('active-text-color');
});

$('#get-product-btn').on('click', () => {
    $.get(`/admin_get_product_details/${$('#edit-form-id').val()}`, (data) => {
        var date = new Date(data['details']['release_date']);
        var imageArray = Array.from(data['images'].map((filepath) => {
            return staticPrefix + filepath;
        }));

        setThumbnail({imageArray: imageArray, index: 0});
        imageArray.forEach((image, index) => {
            setImageChoices(image, index);
        });

        $('#edit-form-name').val(data['details']['name']);
        $('#edit-form-price').val(data['details']['price']);
        $('#edit-form-stock').val(data['details']['stock']);
        $('#edit-form-release').val(
            `${date.getFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-` +
            `${String(date.getUTCDate()).padStart(2, '0')}`
        );
        $('#edit-form-description').val(data['details']['description']);
        $('#edit-form-tags').val(data['tags'].join(', '));
    });
});

$('.delete-product-btn').on('click', function() {
    var message = `Are you sure you want to delete "${$(this).parent().find('#product-name').html().trim()}"?`
    if (confirm(message) == true) {
        $.post(
            '/admin_delete_product', 
            {
                productId: $(this).attr('id'),
            },
        ).done(
            (response) => {
                alert(response);
                $(this).parent().remove();
            }
        ).fail(
            (jqXHR) => {
                alert(jqXHR.responseText);
            }
        );
    }
});

$('#product-form').on('submit', function(event) {
    event.preventDefault();
    $.ajax({
        url: $(this).attr('action'),
        type: 'POST',
        data: new FormData($(this)[0]),
        processData: false,
        contentType: false,
        success: () => {
            alert('Success!')
            $('#search-btn').trigger('click');
        },
        error: (jqXHR) => {
            alert(jqXHR.responseText);
        }
    });

})

$('#search-field').on('keydown', (event) => {
    if (event.key == 'Enter') {
        $('#search-btn').trigger('click');
    }
})

$('#search-btn').on('click', () => {
    var searchQuery = $('#search-field').val();
    $.get(
        `/search_products/${searchQuery}`,
        (data) => {
            var products = Array.from(data);

            $('#listings').html('');
            products.forEach((product) => {
                $('#listings').append(`
                    <div class="d-flex flex-column border rounded product-listing mx-4 mb-3">
                        <button 
                            id="${product['id']}" 
                            class="delete-product-btn delete-btn btn btn-danger m-2">
                                Delete
                        </button>
                        <a class="listing-anchor" href="/product/${product['id']}">
                            <img
                                src="/static/${product['image']}"
                                class="img-thumbnail product-image product-image-small">
                            <div class="d-flex flex-column px-2 pb-2 fill-width">
                                <span data-bs-toggle="tooltip" data-bs-placement="top" title="${product['name']}">
                                    <div id="product-name" class="product-listing-name">
                                    ${product['name']}
                                    </div>
                                </span>
                                <div class="d-flex justify-content-between listing-other-metadata">
                                    <p>
                                        ID: ${product['id']}
                                    </p>
                                    <p>
                                        ${product['tags'][0]} | ${product['tags'][1]}
                                    </p>
                                </div>
                                <hr>
                                <div class="d-flex justify-content-between align-items-end py-2">
                                    <div class="listing-price">
                                        ₱ ${product['price']}
                                    </div>
                                    <div>
                                        Stock: ${product['stock']}
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                `);
            });
            initializeTooltips();
        }
    );
});
