<template>
<v-form v-ref:form :fields="fields" :model="organization"></v-form>
</template>

<script>
import Organization from 'models/organization';
import VForm from 'components/form/vertical-form.vue';
import config from '../../config';

export default {
    components: {VForm},
    props: {
        organization: {
            type: Object,
            default: function() {
                return new Organization();
            }
        },
    },
    data() {
        return {
            fields: [{
                    id: 'name',
                    label: this._('Name')
                }, {
                    id: 'acronym',
                    label: this._('Acronym')
                }, 
                // {
                //     id: 'business_number_id',
                //     label: this._('Business id') +
                //          (config.org_bid_format ? ' (' + config.org_bid_format.toUpperCase() + ')' : '')
                // },
                 {
                    id: 'description',
                    label: this._('Description')
                }, {
                    id: 'url',
                    label: this._('Website'),
                    widget: 'url-field',
                }]
        };
    },
    methods: {
        serialize() {
            return this.$refs.form.serialize();
        },
        validate() {
            return this.$refs.form.validate();
        },
        on_error(response) {
            return this.$refs.form.on_error(response);
        },
    }
};
</script>
