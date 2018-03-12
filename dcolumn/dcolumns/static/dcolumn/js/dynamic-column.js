/*
 * dynamic-column.js
 *
 * Requires: inheritance.js
 *
 * Carl J. Nobile
 *
 * This class will detect what type of field is needed and mutate the current
 * input tag to the correct type. It is designed for a Django admin only.
 *
 * Thanks to: Aurelio De Rosa for trim functions
 *            (http://www.sitepoint.com/trimming-strings-in-javascript/)
 */

"use strict";

String.prototype.trimLeft = function(charlist) {
  if (charlist === undefined)
    charlist = "\s";

  return this.replace(new RegExp("^[" + charlist + "]+"), "");
};

String.prototype.trimRight = function(charlist) {
  if (charlist === undefined)
    charlist = "\s";

  return this.replace(new RegExp("[" + charlist + "]+$"), "");
};

String.prototype.trim = function(charlist) {
  return this.trimLeft(charlist).trimRight(charlist);
};

(function($) {
  var DynamicColumn = Class.extend({
    ADMIN_KEYVALUE_CLASS: "td.field-dynamic_column select",

    init: function(msg, uri) {
      this.uri = uri;
      this.data = null;
      this._initFlag = false;
      this._sendDynamicColumnRequest();
      this._selectCount = 0;
      this._changeClass = this.ADMIN_KEYVALUE_CLASS;
      this._setupAdmin();
      this._checkId = setInterval(this._checkForResponse.bind(this), 200);
    },

    _checkForResponse: function() {
      if(this.data !== null) {
        clearTimeout(this._checkId);
        this._initFlag = true;
        $(this._changeClass).trigger('change');
        this._initFlag = false;
      }
    },

    _setupAdmin: function() {
      setInterval(this._setBindings.bind(this), 100);
    },

    _setBindings: function() {
      var $select = $(this.ADMIN_KEYVALUE_CLASS);
      var oldCount = this._selectCount;
      this._selectCount = $select.length;

      // Only update the bindings when the number of objects change.
      if(oldCount != this._selectCount) {
        //console.log("" + oldCount + " " + this._selectCount);
        $select.off('change', this._determineColumnType);
        $select.on('change', {self: this}, this._determineColumnType);
      }
    },

    _csrfSafeMethod: function(method) {
      // These HTTP methods do not require CSRF protection.
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
     },

    _setHeader: function() {
      $.ajaxSetup({
        crossDomain: false,
        beforeSend: function(xhr, settings) {
          if (!this._csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
          }
        }.bind(this)
      });
    },

    /* Get the dynamic columns */
    _sendDynamicColumnRequest: function() {
      var modelName = $('div.breadcrumbs').children().last().attr('href')
          .trim('/').split(/[\/]/);
      modelName = modelName[modelName.length-1];
      var options = {
        url: this._assembleURI(this.uri + modelName + "/"),
        cache: false,
        type: 'GET',
        contentType: 'json',
        timeout: 20000, // 20 seconds
        //error: this._errorCB.bind(this),
        success: this._dynamicColumnCB.bind(this),
        statusCode: {400: this._dynamicColumnCB.bind(this)}
      };
      this._setHeader();
      $.ajax(options);
    },

    _dynamicColumnCB: function(json, status) {
      if(json.valid) {
        this.data = json;
      } else {
        this._mimicDjangoErrors(json.message, '.errornote');
      }
    },

    _determineColumnType: function(event) {
      var self = event.data.self;

      if(self._initFlag === false) {
        $('.errornote').remove();
        $('.errorlist').remove();
      }

      var cType = $(this).find(':selected').attr('value');
      var relation = self.data.relations[cType];
      var $td = $(this).closest('td').next();
      var $input = $td.find('input, textarea, select');
      var value = $input.attr('value') || $input.text();
      var id = $input.attr('id');
      var name = $input.attr('name');
      var $obj = null;
      var value_type = 6; // This is the default type.

      if(relation !== undefined) {
        value_type = relation.value_type;
      }

      switch(value_type) {
        case 1: // Boolean
          $obj = $('<select id="' + id +'" name="' + name + '"></select>');
          var data = [[0, "No"], [1, "Yes"],];
          var option = "<option></option>";
          var $option = null;

          for(var i = 0; i < data.length; i++) {
            $option = $(option);
            $option.val(data[i][0]);
            $option.text(data[i][1]);
            $option.appendTo($obj);
          }

          break;
        case 2: // Choice
          if(relation.store_relation) {
            if(value === undefined || value === "") {
              value = 0;
            }

            if(value === 0 || self._isInOptions(relation.slug, value)) {
              $obj = self._choiceSelect(id, name, relation.slug);
              value = self._getOptionId(relation.slug, value);
            } else {
              $obj = $('<span id="' + id + '" name="' + name + '">' + value +
                '</span>');
            }
          } else {
            $obj = self._choiceSelect(id, name, relation.slug);
          }

          break;
        case 3: // Date
          $obj = $('<input class="vDateField" id="' + id + '" name="' + name +
            '" type="date" />');
          break;
        case 4: // Datetime
          $obj = $('<input class="vDateField" id="' + id + '" name="' + name +
            '" type="datetime" />');
          break;
        case 5: // Float
          $obj = $('<input id="' + id + '" name="' + name +
            '" type="text" />');
          break;
        case 6: // Number
          $obj = $('<input id="' + id + '" name="' + name +
            '" type="number" />');
          break;
        case 7: // Text
          $obj = $('<input id="' + id + '" name="' + name +
            '" type="text" />');
          break;
        case 8: // Text Block
          $obj = $('<textarea class="vLargeTextField" id="' + id +
            '" name="' + name + '" cols="40" rows="10"></textarea>');
          break;
        case 9: // Time
          $obj = $('<input class="vTimeField" id="' + id + '" name="' + name +
            '" type="time" />');
          break;
        default: // Text
          $obj = $('<input id="' + id + '" name="' + name +
            ' type="text" />');
          break;
      }

      $obj.val(value);
      $input.replaceWith($obj);
    },

    _getOptionId: function(slug, value) {
      var options = this.data.dynamicColumns[slug];
      var result = value;

      for(var i = 0; i < options.length; i++) {
        if(value == options[i][0]) {
          break;
        } else if (value == options[i][1]) {
          result = options[i][0];
          break;
        }
      }

      return result;
    },

    _isInOptions: function(slug, value) {
      var options = this.data.dynamicColumns[slug];
      var result = false;

      for(var i = 0; i < options.length; i++) {
        if(value == options[i][0] || value == options[i][1]) {
          result = true;
          break;
        }
      }

      return result;
    },

    _choiceSelect: function(id, name, slug) {
      var $obj = $('<select id="' + id + '" name="' + name + '"></select>');

      /*
       * Get options from self.data.dynamicColumn using 'slug' and
       * add these options to the select.
       */
      var option = "<option></option>";
      var options = this.data.dynamicColumns[slug];
      var $option = null;

      if(options === undefined) {
        var msg = "Invalid relationship make a note of the steps that " +
                  "led to this error and send them in a bug report.";
        var data = {};
        data[name] = [msg];
        this._mimicDjangoErrors(data, '.errornote');
      } else {
        for(var i = 0; i < options.length; i++) {
          $option = $(option);
          $option.val(options[i][0]);
          $option.text(options[i][1]);
          $option.appendTo($obj);
        }
      }

      return $obj;
    },

    _mimicDjangoErrors: function(data, elm) {
      // Mimic Django error messages.
      var ul = '<ul class="errorlist"></ul>';
      var li = '<li></li>';
      var $tag = null, $errorUl = null, $errorLi = null;

      for(var key in data) {
        $tag = $('select[name=' + key + '], input[name=' + key +
                 '], textarea[name=' + key + ']');
        $errorUl = $(ul);

        if($tag.prev().prop('tagName') === 'LABEL') {
          $tag = $tag.prev();
          $errorUl.insertBefore($tag);
        } else if($tag.length === 0) {
          $tag = $(elm);
          $errorUl.appendTo($tag);
        }

        for(var i = 0; i < data[key].length; i++) {
          $errorLi = $(li);
          $errorLi.html(data[key][i]);
          $errorLi.appendTo($errorUl);
        }
      }
    },

    _assembleURI: function(path) {
      return location.protocol + '//' + location.host + path;
    }
  });


  $(document).ready(function() {
    var msg = '';
    var uri = '/dcolumns/api/collections/';
    new DynamicColumn(msg, uri);
  });
})(django.jQuery);
