/*
 * column-collection.js
 *
 * Requires: inheritance.js
 *
 * Carl J. Nobile
 *
 * This class shows a message at the top of the Column Collection admin page
 * if there are no Dynamic Columns to choose from. It is designed for a Django
 * admin only.
 */

(function($) {
  'use strict';

  var ColumnCollection = Class.extend({
    _MESSAGE: "No objects in the database, please create additional objects " +
        "in the Dynamic Columns model to be used for this collection type.",

    init: function() {
      this._checkForDynamicColumns();
    },

    _checkForDynamicColumns: function() {
      if(!$('#changelist').length && !this._hasDynamicColumns() &&
         !$('ul.errorlist').length) {
        var ul = '<ul class="collection-message"><li>' +
            this._MESSAGE + '</li></ul>';
        $('h1:last').before(ul);
      }
    },

    _hasDynamicColumns: function() {
      var $options = $('.selector-available select.filtered option');

      if($options.length !== 0) {
        return true;
      } else {
        return false;
      }
    }
  });


  $(document).ready(function() {
    // Runs the script after the page has fully loaded.
    $(window).load(function() {
      new ColumnCollection();
    });
  });
})(django.jQuery);
