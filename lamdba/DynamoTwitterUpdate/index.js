console.log('Loading event');
var AWS = require('aws-sdk'); AWS.config.update({region: 'us-east-1'});
var async = require('async');
var request = require('request');
var s3 = new AWS.S3();
var db = new AWS.DynamoDB();
var image = "";
var formData = {
    'tile': '1',
    'use': '1'
};
function detectImageEvent(record, callback) {
    if (record.s3.object.key.indexOf("apod.png") > -1) {
        callback(true);
    }
}

function updateTwitterUser(user, callback) {
    var oauth = {
        consumer_key: '',
        consumer_secret: '',
        token: user.key.S,
        token_secret: user.secret.S
    };
    request.post({
        url: "https://api.twitter.com/1.1/account/update_profile_background_image.json",
        oauth: oauth,
        formData: formData
    }, function(error, response, body) {
        if (error) {
            console.log(error, error.stack);
            callback(false);
        } else if (response.statusCode > 400) {
            console.log(response, body);
            callback(false);
        } else {
            console.log(user.username.S + ": updated");
            callback(true);
        }
    });
}

exports.handler = function(event, context) {
    var ctx = context;
    if (event.Records === null || event.Records === undefined) {
        context.done(null, "bad event");
    }
    async.detect(event.Records, detectImageEvent, function(result) {
        if (result !== undefined) {
            s3.getObject({Bucket: 'apod-twitter', Key: 'apod.png'}, function(err, data) {
                if (err) {
                    ctx.done(err, err.stack);
                }
                formData.image = {
                    value: data.Body,
                    options: {
                        filename: 'apod.png',
                        contentType: 'image/png'
                    }
                };
                db.scan({TableName: "users"}, function(err, data) {
                    if (err === null) {
                        async.every(data.Items, updateTwitterUser, function(result) {
                            if (result) {
                                ctx.done(null, "users updated");
                            } else {
                                ctx.done("got into error making request", "got into error making request");
                            }
                        });
                    } else {
                        ctx.done(err, err.stack);
                    }
                });
            });
        } else {
            context.done(null, "no image");
        }
    });
};