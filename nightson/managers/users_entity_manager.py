from __future__ import absolute_import

from nightson.managers.base_entity_manager import BaseEntityManager
from tornado import gen
import bcrypt

class UsersEntityManager(BaseEntityManager):

    def __init__(self):
        pass

    def __init__(self, request):
        super(UsersEntityManager, self).__init__(request)

    @gen.coroutine
    def fetch_one(self):
        ''' returns one event given an id '''
        id = self.get_value('id')
        sql = ''' SELECT
                  id,
                  first_name,
                  last_name,
                  email,
                  photo_url,
                  phone,
                  ST_AsGeoJson(location) AS location,
                  location_recorded_at,
                  created_at,
                  deleted_at,
                  updated_at
                  FROM Users WHERE id={};
            '''.format(id)
        cursor = yield self.execute_sql(sql)
        raise gen.Return(cursor.fetchone())

    @gen.coroutine
    def update(self):
        ''' updates a given event and returns the updated object!'''

        update_sql = ''' UPDATE Users SET
                          (
                              first_name,
                              last_name,
                              email,
                              photo_url,
                              phone,
                              location,
                              location_recorded_at,
                              created_at
                            )
                            =
                            (
                              '{0}',
                              '{1}',
                              '{2}',
                              '{3}',
                              '{4}',
                              ST_GeomFromText('POINT({5} {6})', 4326),
                              to_timestamp({7}),
                              now()
                            ) where id = {8};
                    '''.format(self.get_value('first_name'),
                               self.get_value('last_name'),
                               self.get_value('email'),
                               self.get_value('photo_url'),
                               self.get_value('phone'),
                               self.get_value('longitude'),
                               self.get_value('latitude'),
                               self.get_value('location_recorded_at'),
                               self.get_value('id')
                       )
        yield self.execute_sql(update_sql)

        ''' query the updated record and return it back!'''
        result = yield self.fetch_one()
        raise gen.Return(result)

    @gen.coroutine
    def insert(self):
        ''' insert a given into and returns the inserted object!'''

        hashed_password = bcrypt.hashpw(self.get_value('password'), bcrypt.gensalt())
        insert_sql = ''' INSERT INTO Users
                            (
                              first_name,
                              last_name,
                              email,
                              photo_url,
                              password,
                              phone,
                              location,
                              location_recorded_at,
                              created_at
                            )
                            VALUES
                            (
                              '{0}',
                              '{1}',
                              '{2}',
                              '{3}',
                              '{4}',
                              '{5}',
                              ST_GeomFromText('POINT({6} {7})', 4326),
                              to_timestamp({8}),
                              now()
                            )
                            RETURNING
                            id,
                            first_name,
                            last_name,
                            email,
                            photo_url,
                            phone,
                            ST_AsGeoJson(location) as location,
                            location_recorded_at,
                            created_at,
                            deleted_at,
                            updated_at
                            ;
                    '''.format(self.get_value('first_name'),
                            self.get_value('last_name'),
                            self.get_value('email'),
                            self.get_value('photo_url'),
                            hashed_password,
                            self.get_value('phone'),
                            self.get_value('longitude'),
                            self.get_value('latitude'),
                            self.get_value('location_recorded_at')
                    )
        cursor = yield self.execute_sql(insert_sql)
        raise gen.Return(cursor.fetchone())

    @gen.coroutine
    def update_password(self, current_user):
        old_password = self.get_value('old_password')
        sql = ''' SELECT id, email, password FROM Users WHERE id = '{0}'; '''.format(current_user.get('id'))

        cursor = yield self.execute_sql(sql)
        result = cursor.fetchone()
        hashed_password = result.get('password')

        result = {}
        if(bcrypt.hashpw(old_password, hashed_password) == hashed_password):
            new_hashed_password = bcrypt.hashpw(self.get_value('new_password'), bcrypt.gensalt())
            update_password_sql = ''' UPDATE Users SET
                                        (
                                          password
                                        ) =
                                        (
                                          '{0}'
                                        )
                                '''.format(new_hashed_password)
            yield self.execute_sql(update_password_sql)
            result = {
                'password': 'update successful!'
            }
        raise gen.Return(result)

    @gen.coroutine
    def update_location(self, current_user):
        latitude = self.get_value('latitude')
        longitude = self.get_value('longitude')
        user_id = current_user.get('id')

        update_location_sql = ''' UPDATE Users SET
                    (location)
                    =
                    (ST_GeomFromText('POINT({0} {1})', 4326))
                    WHERE id = {2}'''.format(longitude, latitude, user_id)

        yield self.execute_sql(update_location_sql)
        result = {
            'location': 'update successful!'
        }
        raise gen.Return(result)



