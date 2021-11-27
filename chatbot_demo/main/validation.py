from marshmallow import Schema, fields, pre_load

from main.utils import Weekday


class BusinessCalendar(Schema):
    date = fields.Date(required=True, format='%d/%m/%Y')
    is_working_day = fields.Bool(required=True)
    office_hr_begin = fields.Time(format='%H:%M', allow_none=True)
    office_hr_end = fields.Time(format='%H:%M', allow_none=True)
    chatting_office_hr_begin = fields.Time(format='%H:%M', allow_none=True)
    chatting_office_hr_end = fields.Time(format='%H:%M', allow_none=True)

    @staticmethod
    def _convert_day(data):
        data['is_working_day'] = True
        if data['day'] == Weekday.PUBLIC_HOLIDAY:
            data['is_working_day'] = False
        data.pop('day')
        return data

    @staticmethod
    def _handle_empty_str(data):
        data['office_hr_begin'] = None if data['office_hr_begin'] == '' else data['office_hr_begin']
        data['office_hr_end'] = None if data['office_hr_end'] == '' else data['office_hr_end']
        data['chatting_office_hr_begin'] = None \
            if data['chatting_office_hr_begin'] == '' else data['chatting_office_hr_begin']
        data['chatting_office_hr_end'] = None \
            if data['chatting_office_hr_end'] == '' else data['chatting_office_hr_end']
        return data

    @pre_load
    def pre_handling(self, data, **kwargs):
        data = self._convert_day(data)
        data = self._handle_empty_str(data)

        return data


business_calendar_schema = BusinessCalendar()
