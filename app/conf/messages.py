from enum import Enum


class Msg(Enum):
    m_409_conflict = 'This email is already in use.'
    m_404_user_not_found = 'User Not Found.'
    m_404_file_not_found = 'File Not Found.'
    m_401_credentials = 'Could not validate credentials.'
    m_401_unauthorized = 'Invalid username or password.'
    m_403_forbidden = 'Operation forbidden.'
    m_403_user_banned = 'User is banned.'
    m_400_inactive_user = 'Inactive user.'
    m_403_not_pdf = 'only PDF file can be downloaded.'
    m_403_foreign_file = 'You can look only own PDF fille.'
