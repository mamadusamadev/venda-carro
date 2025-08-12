class Team():
    def __init__(self, first_name, last_name, designation, photo, facebock_link, twiter_link, google_plus_link):
        
        self.__first_name = first_name
        self.__last_name = last_name
        self.__designation = designation
        self.__photo = photo
        self.__facebock_link = facebock_link
        self.__twiter_link = twiter_link
        self.__google_plus_link = google_plus_link



    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        self.__first_name = first_name
        


    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        self.__last_name = last_name


    @property
    def designation(self):
        return self.__designation

    @designation.setter
    def designation(self, designation):
        self.__designation = designation


    @property
    def photo(self):
        return self.__photo

    @photo.setter
    def photo(self, photo):
        self.__photo = photo



    @property
    def facebock_link(self):
        return self.__facebock_link

    @facebock_link.setter
    def facebock_link(self, facebock_link):
        self.__facebock_link = facebock_link


    @property
    def twiter_link(self):
        return self.__twiter_link

    @twiter_link.setter
    def twiter_link(self, twiter_link):
        self.__twiter_link = twiter_link


    @property
    def google_plus_link(self):
        return self.__google_plus_link

    @google_plus_link.setter
    def google_plus_link(self, google_plus_link):
        self.__google_plus_link = google_plus_link
