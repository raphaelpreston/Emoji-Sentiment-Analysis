
/*
config
 */

(function() {
  var STREAMER, Tweet, drawEmojiStats, emojistatic_css_uri, emojistatic_img_path, formattedTweet, get_cached_selectors, incrementMultipleScores, incrementScore, initDiscoMode, p, processDetailTweetUpdate;

  this.css_animation = true;

  this.use_cached_selectors = true;

  this.replace_technique = false;

  this.reflow_technique = false;

  this.timeout_technique = true;

  this.use_css_sheets = true;

  this.use_capped_stream = true;

  this.force_stream_close = false;

  emojistatic_img_path = 'http://emojistatic.github.io/images/32/';

  emojistatic_css_uri = 'http://emojistatic.github.io/css-sheets/emoji-32px.min.css';


  /*
  inits
   */

  this.score_cache = {};

  this.selector_cache = {};

  this.iOS = false;

  p = navigator.platform;

  if (p === 'iPad' || p === 'iPhone' || p === 'iPod' || p === 'iPhone Simulator' || p === 'iPad Simulator') {
    this.iOS = true;
  }


  /*
  methods related to the polling UI
   */

  this.WEB_API = $('html').data('api-uri') || "/api";

  this.refreshUIFromServer = function(callback) {
    return $.get("" + WEB_API + "/rankings", function(response) {
      return drawEmojiStats(response, callback);
    }, "json");
  };


  /*
  methods related to the streaming UI
   */

  STREAMER = '';

  this.setStreamServerFromEnvironment = function() {
    var rand, server, servers;
    server = $('html').data('stream-server');
    console.log("Environment is setting stream server to " + server);
    servers = server.split(',');
    if (servers.length > 1) {
      console.log("Multiple stream servers in rotation; randomly selecting for client");
      rand = servers[Math.floor(Math.random() * servers.length)];
      console.log("Randomly selected stream server: " + rand);
      return STREAMER = rand;
    } else {
      return STREAMER = server !== '/' ? server : '';
    }
  };

  this.startScoreStreaming = function() {
    if (use_capped_stream) {
      return startCappedScoreStreaming();
    } else {
      return startRawScoreStreaming();
    }
  };

  this.startRawScoreStreaming = function() {
    console.log("Subscribing to score stream (raw)");
    this.source = new EventSource("" + STREAMER + "/subscribe/raw");
    return this.source.onmessage = function(event) {
      return incrementScore(event.data);
    };
  };

  this.startCappedScoreStreaming = function() {
    console.log("Subscribing to score stream (60eps rollup)");
    this.source = new EventSource("" + STREAMER + "/subscribe/eps");
    return this.source.onmessage = function(event) {
      return incrementMultipleScores(event.data);
    };
  };

  this.stopScoreStreaming = function(async) {
    if (async == null) {
      async = true;
    }
    console.log("Unsubscribing to score stream");
    this.source.close();
    if (this.force_stream_close) {
      return forceCloseScoreStream(async);
    }
  };

  this.startDetailStreaming = function(id) {
    console.log("Subscribing to detail stream for " + id);
    this.detail_id = id;
    this.detail_source = new EventSource("" + STREAMER + "/subscribe/details/" + id);
    return this.detail_source.addEventListener("stream.tweet_updates." + id, processDetailTweetUpdate, false);
  };

  this.stopDetailStreaming = function(async) {
    if (async == null) {
      async = true;
    }
    console.log("Unsubscribing to detail stream " + this.detail_id);
    this.detail_source.close();
    if (this.force_stream_close) {
      return forceCloseDetailStream(this.detail_id, async);
    }
  };

  this.forceCloseDetailStream = function(id, async) {
    if (async == null) {
      async = true;
    }
    console.log("Forcing disconnect cleanup for " + id + "...");
    $.ajax({
      type: 'POST',
      url: "" + STREAMER + "/subscribe/cleanup/details/" + id,
      success: function(data) {
        return console.log(" ...Received " + (JSON.stringify(data)) + " from server.");
      },
      async: async
    });
    return true;
  };

  this.forceCloseScoreStream = function(async) {
    if (async == null) {
      async = true;
    }
    console.log("Forcing disconnect cleanup for score stream...");
    $.ajax({
      type: 'POST',
      url: "" + STREAMER + "/subscribe/cleanup/scores",
      success: function(data) {
        return console.log(" ...Received " + (JSON.stringify(data)) + " from server.");
      },
      async: async
    });
    return true;
  };

  // -- Added by Raphael
  allTweets = [];
  downloadIter = 500;
  downloadedCount = 0;
  // --
  processDetailTweetUpdate = function(event) {
    // --- Added by Raphael
    allTweets.push(JSON.parse(event.data).text);
    l = allTweets.length;
    if (l % downloadIter == 0) {
      console.log("Hit " + downloadIter + ". Downloading tweets and resetting counter.");
      hrefSplit = window.location.href.split("/");
      emojiName = hrefSplit[hrefSplit.length - 1];
      console.save(allTweets, emojiName.toString() + "_" + downloadedCount + ".json");
      downloadedCount++;
      allTweets = [];
      console.log("Total batches downloaded: " + downloadedCount)
    }
    // ---
    return appendTweetList($.parseJSON(event.data), true);
  };


  /*
  index page UI helpers
   */

  drawEmojiStats = function(stats, callback) {
    var emoji_char, selector, _fn, _i, _len;
    selector = $("#data");
    selector.empty();
    _fn = function(emoji_char) {
      this.score_cache[emoji_char.id] = emoji_char.score;
      return selector.append("<a href='/details/" + emoji_char.id + "' title='" + emoji_char.name + "' data-id='" + emoji_char.id + "'> <li class='emoji_char' id='" + emoji_char.id + "' data-title='" + emoji_char.name + "'> <span class='char emojifont'>" + (emoji.replace_unified(emoji_char.char)) + "</span> <span class='score' id='score-" + emoji_char.id + "'>" + emoji_char.score + "</span> </li> </a>");
    };
    for (_i = 0, _len = stats.length; _i < _len; _i++) {
      emoji_char = stats[_i];
      _fn(emoji_char);
    }
    if (callback) {
      return callback();
    }
  };

  get_cached_selectors = function(id) {
    var container_selector, score_selector;
    if (this.selector_cache[id] !== void 0) {
      return [this.selector_cache[id][0], this.selector_cache[id][1]];
    } else {
      score_selector = document.getElementById("score-" + id);
      container_selector = document.getElementById(id);
      this.selector_cache[id] = [score_selector, container_selector];
      return [score_selector, container_selector];
    }
  };

  incrementMultipleScores = function(data) {
    var key, scores, value, _results;
    scores = $.parseJSON(data);
    _results = [];
    for (key in scores) {
      value = scores[key];
      _results.push(incrementScore(key, value));
    }
    return _results;
  };

  incrementScore = function(id, incrby) {
    var container_selector, new_container, score_selector, _ref;
    if (incrby == null) {
      incrby = 1;
    }
    if (this.use_cached_selectors) {
      _ref = get_cached_selectors(id), score_selector = _ref[0], container_selector = _ref[1];
    } else {
      score_selector = document.getElementById("score-" + id);
      container_selector = document.getElementById(id);
    }
    score_selector.innerHTML = (this.score_cache[id] += incrby);
    if (css_animation) {
      if (replace_technique) {
        new_container = container_selector.cloneNode(true);
        new_container.classList.add('highlight_score_update_anim');
        container_selector.parentNode.replaceChild(new_container, container_selector);
        if (use_cached_selectors) {
          return selector_cache[id] = [new_container.childNodes[3], new_container];
        }
      } else if (reflow_technique) {
        container_selector.classList.remove('highlight_score_update_anim');
        container_selector.focus();
        return container_selector.classList.add('highlight_score_update_anim');
      } else if (timeout_technique) {
        container_selector.classList.add('highlight_score_update_trans');
        return setTimeout(function() {
          return container_selector.classList.remove('highlight_score_update_trans');
        });
      }
    }
  };


  /*
  detail page/view UI helpers
   */

  this.emptyTweetList = function() {
    var tweet_list;
    tweet_list = $('#tweet_list');
    return tweet_list.empty();
  };

  this.appendTweetList = function(tweet, new_marker) {
    var new_entry, tweet_list, tweet_list_elements;
    if (new_marker == null) {
      new_marker = false;
    }
    tweet_list = $('#tweet_list');
    tweet_list_elements = $("#tweet_list li");
    if (tweet_list_elements.size() >= 20) {
      tweet_list_elements.last().remove();
    }
    new_entry = $(formattedTweet(tweet, new_marker));
    new_entry.find('time.timeago').timeago();
    tweet_list.prepend(new_entry);
    if (css_animation) {
      return new_entry.focus();
    }
  };


  /*
  general purpose UI helpers
   */

  String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };


  /*
  tweet clientside helper and formatting
  BE SURE TWITTER-TEXT-JS is loaded before this!! (TODO: investigate require.js)
   */

  Tweet = (function() {
    function Tweet(status) {
      this.status = status;
    }

    Tweet.prototype.text = function() {
      return twttr.txt.autoLink(this.status.text, {
        urlEntities: this.status.links,
        usernameIncludeSymbol: true,
        targetBlank: true
      });
    };

    Tweet.prototype.url = function() {
      return "https://twitter.com/" + this.status.screen_name + "/status/" + this.status.id;
    };

    Tweet.prototype.profile_url = function() {
      return "https://twitter.com/" + this.status.screen_name;
    };

    Tweet.prototype.profile_image_url = function() {
      if (this.status.profile_image_url == null) {
        return "http://a0.twimg.com/sticky/default_profile_images/default_profile_4_mini.png";
      }
      return this.status.profile_image_url.replace('_normal', '_mini');
    };

    Tweet.prototype.created_at = function() {
      if (this.status.created_at == null) {
        return "#";
      }
      return this.status.created_at;
    };

    return Tweet;

  })();

  this.Handlebars.templates = {};

  $(function() {
    return Handlebars.templates.styled_tweet = Handlebars.compile($('#styled-tweet-template').html());
  });

  formattedTweet = function(tweet, new_marker) {
    var context, wrappedTweet;
    if (new_marker == null) {
      new_marker = false;
    }
    wrappedTweet = new Tweet(tweet);
    context = {
      is_new: new_marker && css_animation ? 'new' : '',
      prepared_tweet_text: emoji.replace_unified(wrappedTweet.text()),
      profile_image_url: wrappedTweet.profile_image_url(),
      profile_url: wrappedTweet.profile_url(),
      name: emoji.replace_unified(tweet.name),
      screen_name: tweet.screen_name,
      created_at: wrappedTweet.created_at(),
      url: wrappedTweet.url(),
      id: tweet.id
    };
    return Handlebars.templates.styled_tweet(context);
  };


  /*
  Polling
   */

  this.startRefreshTimer = function() {
    return this.refreshTimer = setInterval(refreshUIFromServer, 3000);
  };

  this.stopRefreshTimer = function() {
    return clearInterval(this.refreshTimer);
  };


  /*
  Shit to dynamically load css-sheets only on browsers that don't properly support emoji fun
   */

  this.loadEmojiSheet = function(css_url) {
    var cssId, head, link;
    cssId = 'emoji-css-sheet';
    if (!document.getElementById(cssId)) {
      head = document.getElementsByTagName('head')[0];
      link = document.createElement('link');
      link.id = cssId;
      link.rel = 'stylesheet';
      link.type = 'text/css';
      link.href = css_url;
      link.media = 'all';
      return head.appendChild(link);
    }
  };


  /*
  A quick way to toggle avatar display for demos
   */

  this.toggleAvatars = function() {
    return $('#detailview, #tweets').toggleClass('disable-avatars');
  };


  /*
  Secret disco mode (easter egg)
   */

  this.enableDiscoMode = function() {
    var start_music;
    this.disco_time = true;
    console.log("woo disco time!!!!");
    $('body').append("<div id='discoball'></div>");
    $('#discoball').focus();
    start_music = function() {
      var canPlayMP3, canPlayOgg;
      this.audio = new Audio();
      canPlayOgg = !!audio.canPlayType && audio.canPlayType('audio/ogg; codecs="vorbis"') !== "";
      canPlayMP3 = !!audio.canPlayType && audio.canPlayType('audio/mpeg; codecs="mp3"') !== "";
      if (canPlayMP3) {
        console.log("can haz play mp3");
        this.audio.setAttribute("src", "/disco/getlucky-64.mp3");
      } else if (canPlayOgg) {
        console.log("can haz play ogg");
        this.audio.setAttribute("src", "/disco/getlucky-64.ogg");
      }
      this.audio.load();
      return this.audio.play();
    };
    setTimeout(start_music, 2000);
    $('body').addClass('disco');
    $('.emoji_char').addClass('disco');
    $('.navbar').addClass('navbar-inverse');
    return $('#discoball').addClass('in-position');
  };

  this.disableDiscoMode = function() {
    var kill_music;
    this.disco_time = false;
    $('#discoball').removeClass('in-position');
    $('.disco').removeClass('disco');
    $('.navbar').removeClass('navbar-inverse');
    kill_music = function() {
      return this.audio.pause();
    };
    return setTimeout(kill_music, 2000);
  };

  initDiscoMode = function() {
    var disco_index, disco_keys;
    this.disco_time = false;
    disco_keys = [68, 73, 83, 67, 79];
    disco_index = 0;
    $(document).keydown(function(e) {
      if (e.keyCode === disco_keys[disco_index++]) {
        if (disco_index === disco_keys.length) {
          return enableDiscoMode();
        }
      } else {
        return disco_index = 0;
      }
    });
    return $(document).keyup(function(e) {
      if (e.keyCode === 27) {
        if (disco_time === true) {
          return disableDiscoMode();
        }
      }
    });
  };


  /*
  Configuration vars we need to set globally
   */

  $(function() {
    emoji.img_path = emojistatic_img_path;
    emoji.init_env();
    console.log("INFO: js-emoji replace mode is " + emoji.replace_mode);
    if (emoji.replace_mode === 'css' && use_css_sheets) {
      console.log("In a browser that supports CSS fanciness but not emoji characters, dynamically injecting css-sheet!");
      emoji.use_css_imgs = true;
      loadEmojiSheet(emojistatic_css_uri);
    }
    setStreamServerFromEnvironment();
    return initDiscoMode();
  });

}).call(this);
